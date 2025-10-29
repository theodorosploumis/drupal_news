#!/bin/bash
##
# Release Script for Drupal News Aggregator
# Creates new version, updates RELEASES.md, creates git tag
##

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
error() {
    echo -e "${RED}✗ Error: $1${NC}" >&2
    exit 1
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Get current version
get_current_version() {
    if [ -f VERSION ]; then
        cat VERSION | tr -d '\n'
    else
        echo "0.0.0"
    fi
}

# Increment version
increment_version() {
    local version=$1
    local type=$2

    IFS='.' read -ra PARTS <<< "$version"
    local major=${PARTS[0]}
    local minor=${PARTS[1]}
    local patch=${PARTS[2]}

    case $type in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            error "Invalid version type: $type (use: major, minor, or patch)"
            ;;
    esac

    echo "$major.$minor.$patch"
}

# Check if working directory is clean
check_clean_working_tree() {
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        error "Working directory is not clean. Commit or stash changes first."
    fi
}

# Check if on main/master branch
check_branch() {
    local branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [[ "$branch" != "main" && "$branch" != "master" ]]; then
        warning "Not on main/master branch (currently on: $branch)"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Update RELEASES.md
update_releases() {
    local version=$1
    local changelog=$2
    local date=$(date +%Y-%m-%d)

    if [ ! -f RELEASES.md ]; then
        cat > RELEASES.md << 'EOF'
# Release Notes

All notable changes to Drupal News Aggregator will be documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

EOF
    fi

    # Create temporary file with new release
    local temp_file=$(mktemp)

    # Add header and existing content
    head -n 5 RELEASES.md > "$temp_file"

    # Add new release
    cat >> "$temp_file" << EOF

## [$version] - $date

$changelog

EOF

    # Add rest of existing releases
    tail -n +6 RELEASES.md >> "$temp_file"

    # Replace original file
    mv "$temp_file" RELEASES.md

    success "Updated RELEASES.md"
}

# Show usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS] <VERSION_TYPE>

Create a new release with git tag and update release notes.

VERSION_TYPE:
  major          Increment major version (X.0.0)
  minor          Increment minor version (0.X.0)
  patch          Increment patch version (0.0.X)
  <version>      Use specific version (e.g., 1.2.3)

OPTIONS:
  -m, --message  Release message/changelog
  -p, --push     Push tag to remote after creating
  -h, --help     Show this help

EXAMPLES:
  $0 patch -m "Bug fixes and improvements"
  $0 minor -m "New features added" --push
  $0 1.2.0 -m "Major release"

WORKFLOW:
  1. Validates working tree is clean
  2. Increments VERSION file
  3. Updates RELEASES.md with changelog
  4. Commits changes
  5. Creates annotated git tag
  6. Optionally pushes to remote

EOF
}

# Main script
main() {
    local version_type=""
    local changelog=""
    local push_tag=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -m|--message)
                changelog="$2"
                shift 2
                ;;
            -p|--push)
                push_tag=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            -*)
                error "Unknown option: $1"
                ;;
            *)
                version_type="$1"
                shift
                ;;
        esac
    done

    # Validate version type
    if [ -z "$version_type" ]; then
        usage
        exit 1
    fi

    # Get changelog if not provided
    if [ -z "$changelog" ]; then
        info "Enter release notes/changelog (Ctrl+D when done):"
        changelog=$(cat)

        if [ -z "$changelog" ]; then
            error "Changelog is required. Use -m or provide via stdin."
        fi
    fi

    info "Drupal News Aggregator - Release Script"
    echo "========================================"
    echo

    # Checks
    info "Checking git repository..."
    check_clean_working_tree
    check_branch
    success "Repository is ready"

    # Get current and new version
    local current_version=$(get_current_version)
    local new_version

    if [[ "$version_type" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        new_version="$version_type"
        info "Using specific version: $new_version"
    else
        new_version=$(increment_version "$current_version" "$version_type")
        info "Incrementing $version_type version"
    fi

    info "Current version: $current_version"
    info "New version: $new_version"
    echo

    # Confirm
    read -p "Continue with release v$new_version? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        warning "Release cancelled"
        exit 0
    fi

    # Update VERSION file
    echo "$new_version" > VERSION
    success "Updated VERSION file"

    # Update RELEASES.md
    update_releases "$new_version" "$changelog"

    # Stage changes
    git add VERSION RELEASES.md
    success "Staged VERSION and RELEASES.md"

    # Commit
    git commit -m "Release v$new_version"
    success "Committed release changes"

    # Create annotated tag
    git tag -a "v$new_version" -m "Release v$new_version

$changelog"
    success "Created git tag v$new_version"

    echo
    success "Release v$new_version created successfully!"
    echo

    # Show what happened
    info "What was done:"
    echo "  • VERSION updated: $current_version → $new_version"
    echo "  • RELEASES.md updated with changelog"
    echo "  • Git commit created"
    echo "  • Git tag created: v$new_version"
    echo

    # Push if requested
    if [ "$push_tag" = true ]; then
        info "Pushing to remote..."
        git push origin $(git rev-parse --abbrev-ref HEAD)
        git push origin "v$new_version"
        success "Pushed tag to remote"
        echo
        info "GitHub Actions will now build and publish to PyPI"
    else
        info "To push the release, run:"
        echo "  git push origin $(git rev-parse --abbrev-ref HEAD)"
        echo "  git push origin v$new_version"
    fi

    echo
    info "Next steps:"
    echo "  1. Push the tag to trigger GitHub Actions"
    echo "  2. Monitor the build at: https://github.com/yourusername/drupal-news/actions"
    echo "  3. Package will be published to PyPI automatically"
}

# Run main
main "$@"
