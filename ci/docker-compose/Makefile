# Set dir of Makefile to a variable to use later
MAKEPATH := $(abspath $(lastword $(MAKEFILE_LIST)))
BASEDIR := $(notdir $(patsubst %/,%,$(dir $(MAKEPATH))))

COMPOSE_FILES := $(wildcard *.yml)
COMPOSE_FILE_ARGS := $(foreach yml,$(COMPOSE_FILES),-f $(yml))

ATTACH_COMPOSE_FILE_ARGS := $(foreach yml,$(filter-out tango.yml,$(COMPOSE_FILES)),-f $(yml))

# If the first make argument is "start" or "stop"...
ifeq (start,$(firstword $(MAKECMDGOALS)))
  SERVICE_TARGET = true
else ifeq (stop,$(firstword $(MAKECMDGOALS)))
  SERVICE_TARGET = true
else ifeq (attach,$(firstword $(MAKECMDGOALS)))
  SERVICE_TARGET = true
ifndef NETWORK_MODE
$(error NETWORK_MODE must specify the network to attach to, e.g., make NETWORK_MODE=tangonet-powersupply ...)
endif
ifndef TANGO_HOST
$(error TANGO_HOST must specify the Tango database device, e.g., make TANGO_HOST=powersupply-databaseds:100000 ...)
endif
endif
ifdef SERVICE_TARGET
  # .. then use the rest as arguments for the make target
  SERVICE := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(SERVICE):;@:)
endif

#
# Never use the network=host mode when running CI jobs, and add extra
# distinguishing identifiers to the network name and container names to
# prevent collisions with jobs from the same project running at the same
# time.
#
ifneq ($(CI_JOB_ID),)
NETWORK_MODE := tangonet-$(CI_JOB_ID)
CONTAINER_NAME_PREFIX := $(CI_JOB_ID)-
else
CONTAINER_NAME_PREFIX :=
$(info Network mode cannot be host for the archiver! It won't work unless you set the env var CI_JOB_ID=local)
endif

ifeq ($(OS),Windows_NT)
    $(error Sorry, Windows is not supported yet)
else
	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Linux)
		DISPLAY ?= :0.0
		NETWORK_MODE ?= host
		XAUTHORITY_MOUNT := /tmp/.X11-unix:/tmp/.X11-unix
		XAUTHORITY ?= /hosthome/.Xauthority
		# /bin/sh (=dash) does not evaluate 'docker network' conditionals correctly
		SHELL := /bin/bash
	endif
	ifeq ($(UNAME_S),Darwin)
		IF_INTERFACE := $(shell scutil --nwi | grep 'Network interfaces:' | cut -d' ' -f3)
		DISPLAY := $(shell scutil --nwi | grep 'address' | cut -d':' -f2 | tr -d ' ' | head -n1):0
		# network_mode = host doesn't work on MacOS, so fix to the internal network
		NETWORK_MODE ?= tangonet
		XAUTHORITY_MOUNT := $(HOME)/.Xauthority:/hosthome/.Xauthority:ro
		XAUTHORITY := /hosthome/.Xauthority
	endif
endif

#
# When running in network=host mode, point devices at a port on the host
# machine rather than at the container.
#
ifeq ($(NETWORK_MODE),host)
	TANGO_HOST := $(shell hostname):10000
	MYSQL_HOST := $(shell hostname):3306
else
	TANGO_HOST := $(CONTAINER_NAME_PREFIX)databaseds:10000
	MYSQL_HOST := $(CONTAINER_NAME_PREFIX)tangodb:3306
endif

DOCKER_COMPOSE_ARGS := DISPLAY=$(DISPLAY) XAUTHORITY=$(XAUTHORITY) TANGO_HOST=$(TANGO_HOST) \
		NETWORK_MODE=$(NETWORK_MODE) XAUTHORITY_MOUNT=$(XAUTHORITY_MOUNT) MYSQL_HOST=$(MYSQL_HOST) \
		CONTAINER_NAME_PREFIX=$(CONTAINER_NAME_PREFIX) COMPOSE_IGNORE_ORPHANS=true


.PHONY: up down minimal start stop status clean pull help
.DEFAULT_GOAL := help

pull: ## pull the images from the Docker hub
	$(DOCKER_COMPOSE_ARGS) docker-compose $(COMPOSE_FILE_ARGS) pull

up: minimal  ## start the base TANGO system and prepare all services
	$(DOCKER_COMPOSE_ARGS) docker-compose $(COMPOSE_FILE_ARGS) up --no-start

down:  ## stop all services and tear down the system
	$(DOCKER_COMPOSE_ARGS) docker-compose $(COMPOSE_FILE_ARGS) down
ifneq ($(NETWORK_MODE),host)
	docker network inspect $(NETWORK_MODE) &> /dev/null && ([ $$? -eq 0 ] && docker network rm $(NETWORK_MODE)) || true
endif

minimal: ## start the base TANGO system
ifneq ($(NETWORK_MODE),host)
	docker network inspect $(NETWORK_MODE) &> /dev/null || ([ $$? -ne 0 ] && docker network create $(NETWORK_MODE))
endif
	$(DOCKER_COMPOSE_ARGS) docker-compose -f tango.yml up -d

start: up ## start a service (usage: make start <servicename>)
	$(DOCKER_COMPOSE_ARGS) docker-compose $(COMPOSE_FILE_ARGS) start $(SERVICE)

stop:  ## stop a service (usage: make stop <servicename>)
	$(DOCKER_COMPOSE_ARGS) docker-compose $(COMPOSE_FILE_ARGS) stop $(SERVICE)

attach:  ## attach a service to an existing Tango network
	$(DOCKER_COMPOSE_ARGS) docker-compose $(ATTACH_COMPOSE_FILE_ARGS) up -d $(SERVICE)

status:  ## show the container status
	$(DOCKER_COMPOSE_ARGS) docker-compose $(COMPOSE_FILE_ARGS) ps

clean: down  ## clear all TANGO database entries
	docker volume rm $(BASEDIR)_tangodb

help:   ## show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

