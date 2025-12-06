# Simple release automation for building, pushing, and deploying to k8s

.PHONY: help build push image set-image deploy rollout publish k8s-apply all docker-login print-image

# Tools (override if needed)
DOCKER ?= docker
KUBECTL ?= kubectl

# Image coordinates
APP_NAME ?= langfuse-demo
REGISTRY ?= registry.baidubce.com
IMAGE_REPO ?= $(REGISTRY)/cprom-stack-dev/$(APP_NAME)
VERSION ?= $(shell git rev-parse --short HEAD 2>/dev/null || date +%Y%m%d%H%M%S)
IMAGE ?= $(IMAGE_REPO):$(VERSION)
LATEST ?= $(IMAGE_REPO):latest

# Kubernetes
NAMESPACE ?= default

help:
	@echo "Targets:"
	@echo "  make build           Build the image $(IMAGE)"
	@echo "  make push            Push the image (both version and latest)"
	@echo "  make set-image       Patch k8s/deployment.yaml with the built image"
	@echo "  make deploy          Apply k8s manifests (config, secret if present, deploy, svc, ingress if present)"
	@echo "  make rollout         Wait for rollout to complete"
	@echo "  make publish         Build + push + set-image + deploy + rollout"
	@echo "Variables: REGISTRY, APP_NAME, VERSION, IMAGE, NAMESPACE"

print-image:
	@echo $(IMAGE)

docker-login:
	$(DOCKER) login

build:
	$(DOCKER) build -t $(IMAGE) .

push: build
	$(DOCKER) push $(IMAGE)

# Carefully replace the image line in deployment.yaml
set-image:
	@[ -f k8s/deployment.yaml ] || { echo "k8s/deployment.yaml not found"; exit 1; }
	sed -i.bak -E 's|^(\s*image:\s*).*$|\1$(IMAGE)|' k8s/deployment.yaml && rm -f k8s/deployment.yaml.bak
	@echo "deployment.yaml updated -> $(IMAGE)"

k8s-apply:
	@$(KUBECTL) apply -n $(NAMESPACE) -f k8s/configmap.yaml
	@if [ -f k8s/secret.yaml ]; then $(KUBECTL) apply -n $(NAMESPACE) -f k8s/secret.yaml; else echo "(skip) k8s/secret.yaml not found"; fi
	@$(KUBECTL) apply -n $(NAMESPACE) -f k8s/deployment.yaml
	@$(KUBECTL) apply -n $(NAMESPACE) -f k8s/service.yaml
	@if [ -f k8s/ingress.yaml ]; then $(KUBECTL) apply -n $(NAMESPACE) -f k8s/ingress.yaml; else echo "(skip) k8s/ingress.yaml not found"; fi

deploy: k8s-apply

rollout:
	$(KUBECTL) rollout status -n $(NAMESPACE) deployment/langfuse-demo

publish: push set-image deploy rollout
	@echo "Published: $(IMAGE)"

