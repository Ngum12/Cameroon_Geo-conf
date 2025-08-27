#!/bin/bash

# Project Sentinel - Container Image Build Script
# Cameroon Defense Force - RESTRICTED
# This script builds and optionally pushes all Docker images for production deployment

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
REGISTRY_URL="${REGISTRY_URL:-registry.cdf.cm}"
IMAGE_TAG="${IMAGE_TAG:-prod}"
PUSH_IMAGES=false
PRODUCTION_BUILD=false

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --production     Build production-optimized images"
    echo "  --push          Push images to registry after building"
    echo "  --tag TAG       Use custom tag (default: prod)"
    echo "  --registry URL  Use custom registry URL (default: registry.cdf.cm)"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --production --push                    # Build and push production images"
    echo "  $0 --tag v1.2.3 --push                   # Build and push with custom tag"
    echo "  $0 --registry my-registry.com --push     # Use custom registry"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --production)
            PRODUCTION_BUILD=true
            shift
            ;;
        --push)
            PUSH_IMAGES=true
            shift
            ;;
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --registry)
            REGISTRY_URL="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            ;;
    esac
done

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
    fi
    
    # Check registry credentials if push is enabled
    if [[ "$PUSH_IMAGES" == true ]]; then
        if [[ -z "${REGISTRY_USERNAME:-}" ]] || [[ -z "${REGISTRY_PASSWORD:-}" ]]; then
            warn "Registry credentials not found. Attempting to use existing Docker credentials."
        else
            log "Logging into registry: $REGISTRY_URL"
            echo "${REGISTRY_PASSWORD}" | docker login "$REGISTRY_URL" --username "$REGISTRY_USERNAME" --password-stdin
        fi
    fi
    
    log "Prerequisites check completed successfully"
}

# Build backend API image
build_backend() {
    log "Building backend API image..."
    
    local dockerfile="backend-api/Dockerfile"
    if [[ "$PRODUCTION_BUILD" == true ]] && [[ -f "backend-api/Dockerfile.prod" ]]; then
        dockerfile="backend-api/Dockerfile.prod"
    fi
    
    docker build \
        --file "$dockerfile" \
        --tag "${REGISTRY_URL}/sentinel/backend:${IMAGE_TAG}" \
        --build-arg BUILD_ENV=production \
        --build-arg VERSION="${IMAGE_TAG}" \
        .
    
    log "Backend API image built successfully"
}

# Build frontend dashboard image
build_frontend() {
    log "Building frontend dashboard image..."
    
    local dockerfile="frontend-dashboard/Dockerfile"
    if [[ "$PRODUCTION_BUILD" == true ]] && [[ -f "frontend-dashboard/Dockerfile.prod" ]]; then
        dockerfile="frontend-dashboard/Dockerfile.prod"
    fi
    
    # Set build arguments for frontend
    local build_args=""
    if [[ -n "${MAPBOX_TOKEN:-}" ]]; then
        build_args="--build-arg VITE_MAPBOX_ACCESS_TOKEN=$MAPBOX_TOKEN"
    fi
    if [[ -n "${API_BASE_URL:-}" ]]; then
        build_args="$build_args --build-arg VITE_API_BASE_URL=$API_BASE_URL"
    fi
    
    docker build \
        --file "$dockerfile" \
        --tag "${REGISTRY_URL}/sentinel/frontend:${IMAGE_TAG}" \
        --build-arg BUILD_ENV=production \
        --build-arg VERSION="${IMAGE_TAG}" \
        $build_args \
        frontend-dashboard/
    
    log "Frontend dashboard image built successfully"
}

# Build translation service image
build_translation() {
    log "Building translation service image..."
    
    docker build \
        --file "nlp-models/Dockerfile" \
        --tag "${REGISTRY_URL}/sentinel/translation:${IMAGE_TAG}" \
        --build-arg MODEL_NAME=facebook/m2m100_418M \
        --build-arg SERVICE_TYPE=translation \
        nlp-models/
    
    log "Translation service image built successfully"
}

# Build NER service image
build_ner() {
    log "Building NER service image..."
    
    local dockerfile="nlp-models/Dockerfile.ner"
    if [[ ! -f "$dockerfile" ]] && [[ -f "nlp-models/ner_dockerfile" ]]; then
        dockerfile="nlp-models/ner_dockerfile"
    fi
    
    docker build \
        --file "$dockerfile" \
        --tag "${REGISTRY_URL}/sentinel/ner:${IMAGE_TAG}" \
        --build-arg MODEL_NAME=xlm-roberta-large-finetuned-conll03-english \
        --build-arg SERVICE_TYPE=ner \
        nlp-models/
    
    log "NER service image built successfully"
}

# Build data ingestion service image
build_ingestion() {
    log "Building data ingestion service image..."
    
    docker build \
        --file "data-ingestion/Dockerfile" \
        --tag "${REGISTRY_URL}/sentinel/ingestion:${IMAGE_TAG}" \
        --build-arg SCRAPY_VERSION=2.11.0 \
        data-ingestion/
    
    log "Data ingestion service image built successfully"
}

# Push images to registry
push_images() {
    if [[ "$PUSH_IMAGES" != true ]]; then
        return 0
    fi
    
    log "Pushing images to registry: $REGISTRY_URL"
    
    local images=(
        "sentinel/backend:${IMAGE_TAG}"
        "sentinel/frontend:${IMAGE_TAG}"
        "sentinel/translation:${IMAGE_TAG}"
        "sentinel/ner:${IMAGE_TAG}"
        "sentinel/ingestion:${IMAGE_TAG}"
    )
    
    for image in "${images[@]}"; do
        log "Pushing ${REGISTRY_URL}/${image}..."
        docker push "${REGISTRY_URL}/${image}"
    done
    
    log "All images pushed successfully"
}

# Tag images with additional tags
tag_images() {
    log "Tagging images..."
    
    local images=(
        "sentinel/backend"
        "sentinel/frontend"
        "sentinel/translation"
        "sentinel/ner"
        "sentinel/ingestion"
    )
    
    # Tag with latest if this is a production build
    if [[ "$PRODUCTION_BUILD" == true ]]; then
        for image in "${images[@]}"; do
            docker tag "${REGISTRY_URL}/${image}:${IMAGE_TAG}" "${REGISTRY_URL}/${image}:latest"
        done
        log "Images tagged with 'latest'"
    fi
    
    # Tag with timestamp
    local timestamp=$(date +%Y%m%d-%H%M%S)
    for image in "${images[@]}"; do
        docker tag "${REGISTRY_URL}/${image}:${IMAGE_TAG}" "${REGISTRY_URL}/${image}:${timestamp}"
    done
    log "Images tagged with timestamp: $timestamp"
}

# Display image information
show_image_info() {
    log "Built images:"
    echo ""
    
    local images=(
        "${REGISTRY_URL}/sentinel/backend:${IMAGE_TAG}"
        "${REGISTRY_URL}/sentinel/frontend:${IMAGE_TAG}"
        "${REGISTRY_URL}/sentinel/translation:${IMAGE_TAG}"
        "${REGISTRY_URL}/sentinel/ner:${IMAGE_TAG}"
        "${REGISTRY_URL}/sentinel/ingestion:${IMAGE_TAG}"
    )
    
    for image in "${images[@]}"; do
        if docker image inspect "$image" &> /dev/null; then
            local size=$(docker image inspect "$image" --format='{{.Size}}' | numfmt --to=iec)
            local created=$(docker image inspect "$image" --format='{{.Created}}' | cut -d'T' -f1)
            echo -e "  ${BLUE}$image${NC}"
            echo -e "    Size: $size, Created: $created"
        fi
    done
    echo ""
}

# Clean up old images
cleanup_images() {
    log "Cleaning up old images..."
    
    # Remove dangling images
    docker image prune -f &> /dev/null || true
    
    # Remove old tagged images (keep last 5 versions)
    local images=(
        "sentinel/backend"
        "sentinel/frontend"
        "sentinel/translation"
        "sentinel/ner"
        "sentinel/ingestion"
    )
    
    for image in "${images[@]}"; do
        # Get image IDs sorted by creation date (oldest first)
        local old_images=$(docker images "${REGISTRY_URL}/${image}" --format "{{.ID}} {{.CreatedAt}}" | sort -k2 | head -n -5 | cut -d' ' -f1)
        
        for image_id in $old_images; do
            docker rmi "$image_id" &> /dev/null || true
        done
    done
    
    log "Cleanup completed"
}

# Main execution function
main() {
    log "🚀 Starting Project Sentinel image build process"
    log "Registry: $REGISTRY_URL"
    log "Tag: $IMAGE_TAG"
    log "Production build: $PRODUCTION_BUILD"
    log "Push images: $PUSH_IMAGES"
    echo ""
    
    check_prerequisites
    
    # Build all images
    build_backend
    build_frontend
    build_translation
    build_ner
    build_ingestion
    
    # Tag images
    tag_images
    
    # Push images if requested
    push_images
    
    # Show built images
    show_image_info
    
    # Cleanup
    cleanup_images
    
    log "🎯 Project Sentinel image build completed successfully!"
    
    if [[ "$PUSH_IMAGES" == true ]]; then
        log "📦 All images have been pushed to: $REGISTRY_URL"
        echo ""
        echo "Next steps:"
        echo "1. Update Kubernetes manifests with new image tags"
        echo "2. Deploy to production cluster"
        echo "3. Verify all services are healthy"
    else
        log "💡 Use --push flag to push images to registry"
    fi
}

# Execute main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
