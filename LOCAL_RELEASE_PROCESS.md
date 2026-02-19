# Local Release Packaging and Direct Upload Process

## 1. Overview

This document outlines the technical specification for implementing a local release packaging workflow that bypasses the current GitHub-based automated packaging process. The goal is to provide a reliable alternative for creating and publishing releases when the automated CI/CD pipeline fails.

## 2. Current Build and Release Process

### 2.1 Existing Build System

The project uses a Makefile-based build system with the following key targets:

- `make build`: Builds for the current platform
- `make build-all`: Builds for all platforms (Windows, Linux, macOS)
- `make release`: Builds for all platforms and creates release archives

### 2.2 Current Release Artifacts

The `make release` target generates the following artifacts in the `release/` directory:

| Platform | Architecture | Archive Format |
|----------|--------------|----------------|
| Windows  | amd64        | .zip           |
| Windows  | arm64        | .zip           |
| Linux    | amd64        | .tar.gz        |
| Linux    | arm64        | .tar.gz        |
| macOS    | amd64        | .tar.gz        |
| macOS    | arm64        | .tar.gz        |

## 3. Proposed Local Packaging Workflow

### 3.1 Prerequisites

- Go 1.21+ installed
- Git installed
- GitHub CLI (`gh`) installed (for direct upload)
- Make (for Windows users, consider using Git Bash or WSL)

### 3.2 Step-by-Step Process

#### 3.2.1 Environment Setup

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/cgartlab/SwiftInstall.git
   cd SwiftInstall
   ```

2. **Ensure dependencies are up-to-date**:
   ```bash
   make deps
   ```

#### 3.2.2 Local Packaging

1. **Create a new release branch** (if applicable):
   ```bash
   git checkout -b release/vX.Y.Z
   ```

2. **Update CHANGELOG.md** with the new version changes:
   ```markdown
   ## [X.Y.Z] - YYYY-MM-DD

   ### Added
   - New features...

   ### Changed
   - Changes...

   ### Fixed
   - Bug fixes...
   ```

3. **Commit CHANGELOG changes**:
   ```bash
   git add CHANGELOG.md
   git commit -m "docs: update CHANGELOG for vX.Y.Z"
   ```

4. **Create and push Git tag**:
   - The version is automatically derived from Git tags using `git describe --tags`
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

5. **Build and package the release**:
   ```bash
   make release
   ```

6. **Verify the artifacts**:
   ```bash
   ls -la release/
   ```
   Ensure all expected archives are present and have reasonable file sizes.

#### 3.2.3 Direct Upload to GitHub Releases

1. **Create a new GitHub Release** using the GitHub CLI:
   ```bash
   gh release create vX.Y.Z --title "Release vX.Y.Z" --notes "See CHANGELOG.md for details"
   ```

2. **Upload the artifacts**:
   ```bash
   gh release upload vX.Y.Z release/*
   ```

3. **Verify the release**:
   - Check the GitHub repository's Releases page to ensure all artifacts were uploaded successfully
   - Download and test one of the artifacts to confirm it works correctly

## 4. Implementation Details

### 4.1 Build Configuration

The build process uses the following environment variables and flags:

- `BINARY_NAME`: Name of the binary (`sis`)
- `VERSION`: Derived from Git tags or set to "dev"
- `COMMIT`: Current Git commit hash
- `DATE`: Current UTC timestamp
- `LDFLAGS`: Linker flags to embed version information

### 4.2 Cross-Platform Building

The Makefile supports cross-compilation for all major platforms:

- Windows: `GOOS=windows GOARCH={amd64,arm64}`
- Linux: `GOOS=linux GOARCH={amd64,arm64}`
- macOS: `GOOS=darwin GOARCH={amd64,arm64}`

### 4.3 Version Management

**Version Tagging Convention:**
- Format: `vMAJOR.MINOR.PATCH` (e.g., `v0.1.7`)
- Use annotated tags: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- Tags should be pushed after committing related changes

**CHANGELOG Management:**
- Update `CHANGELOG.md` before creating a release tag
- Follow the format: `## [X.Y.Z] - YYYY-MM-DD`
- Categorize changes: Added, Changed, Fixed, Removed, Deprecated

## 5. Potential Challenges

### 5.1 Cross-Compilation Issues

- **Windows-specific challenges**: Building for Windows from non-Windows platforms may require additional setup
- **macOS signing**: macOS binaries may need to be signed for distribution
- **Dependency issues**: Some dependencies may have platform-specific requirements

### 5.2 Upload Limitations

- **File size limits**: GitHub has file size limits for releases (currently 2GB per file)
- **Network bandwidth**: Uploading multiple artifacts may be time-consuming on slow connections
- **Authentication**: Ensuring proper GitHub authentication for the `gh` CLI

### 5.3 Versioning Consistency

- **Tag synchronization**: Ensuring Git tags are properly created and pushed before building
- **Version embedding**: Verifying that the correct version information is embedded in the binaries
- **CHANGELOG updates**: Remembering to update CHANGELOG before each release

## 6. Security Considerations

### 6.1 Authentication Security

- **GitHub CLI authentication**: The `gh` CLI stores authentication credentials securely
- **Token management**: Use personal access tokens with appropriate scopes (repo scope for releases)
- **Token rotation**: Regularly rotate GitHub access tokens

### 6.2 Build Environment Security

- **Clean build environment**: Ensure the build environment is free of malware or compromised dependencies
- **Dependency verification**: Use `go mod verify` to ensure dependencies are authentic
- **Code signing**: Consider signing binaries to verify their authenticity

### 6.3 Release Verification

- **Artifact integrity**: Verify checksums of uploaded artifacts
- **Malware scanning**: Consider scanning release artifacts for malware before upload
- **Testing**: Test releases on multiple platforms to ensure they function correctly

## 7. Validation Criteria

### 7.1 Build Success Criteria

- [ ] All platform builds complete without errors
- [ ] All expected release artifacts are generated
- [ ] Artifacts have appropriate file sizes
- [ ] Version information is correctly embedded in binaries
- [ ] CHANGELOG.md is updated with the new version

### 7.2 Upload Success Criteria

- [ ] GitHub Release is created successfully
- [ ] All artifacts are uploaded without errors
- [ ] Artifacts are visible on the GitHub Releases page
- [ ] Download links work correctly

### 7.3 Functionality Validation

- [ ] Binaries run correctly on their respective platforms
- [ ] Basic functionality tests pass
- [ ] Version information is displayed correctly (`sis version`)
- [ ] No regressions from previous releases

## 8. Alternative Approaches

### 8.1 Manual Upload via GitHub Web UI

If the GitHub CLI is not available, artifacts can be uploaded manually via the GitHub web interface:

1. Create a new release on the GitHub repository
2. Drag and drop the artifacts from the `release/` directory to the upload area
3. Complete the release creation process

### 8.2 Scripted Upload Process

For more automation, create a script that combines the build and upload steps:

```bash
#!/bin/bash

# Set version
VERSION="vX.Y.Z"

# Update CHANGELOG (manual step)
echo "Please update CHANGELOG.md before continuing..."
read -p "Press enter to continue..."

# Commit CHANGELOG
git add CHANGELOG.md
git commit -m "docs: update CHANGELOG for $VERSION"

# Create tag
git tag -a $VERSION -m "Release $VERSION"
git push origin $VERSION

# Build and package
make release

# Create release and upload
gh release create $VERSION --title "Release $VERSION" --notes "See CHANGELOG.md for details"
gh release upload $VERSION release/*

echo "Release $VERSION created and uploaded successfully!"
```

## 9. Release Checklist

### Pre-Release
- [ ] All features for this version are complete
- [ ] All tests pass (`go test ./...`)
- [ ] Code is formatted (`go fmt ./...`)
- [ ] CHANGELOG.md is updated
- [ ] README.md is updated (if needed)

### Build & Release
- [ ] CHANGELOG changes are committed
- [ ] Git tag is created and pushed
- [ ] Build completes successfully
- [ ] All artifacts are generated
- [ ] Artifacts are tested on target platforms
- [ ] Release is created on GitHub
- [ ] All artifacts are uploaded

### Post-Release
- [ ] Release page shows all artifacts correctly
- [ ] Download links work
- [ ] Installation scripts work with new version
- [ ] Version command shows correct version

## 10. Conclusion

The local packaging and direct upload process provides a reliable alternative to the automated CI/CD pipeline. By following the steps outlined in this specification, you can create and publish releases consistently, even when the automated process fails.

This approach offers several advantages:

- **Reliability**: Bypasses potentially flaky CI/CD infrastructure
- **Control**: Provides full control over the build and release process
- **Flexibility**: Allows for customizations and troubleshooting
- **Speed**: Can be faster than waiting for CI/CD jobs to complete

With proper implementation and validation, this workflow can become the primary method for creating releases, ensuring consistent delivery of high-quality software to users.

## Quick Reference

```bash
# Quick release commands
git add CHANGELOG.md
git commit -m "docs: update CHANGELOG for vX.Y.Z"
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
make release
gh release create vX.Y.Z --title "Release vX.Y.Z" --notes "See CHANGELOG.md"
gh release upload vX.Y.Z release/*
```
