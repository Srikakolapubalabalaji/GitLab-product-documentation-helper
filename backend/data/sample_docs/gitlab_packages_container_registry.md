# GitLab Container Registry and Package Registry Documentation

Source URL: https://docs.gitlab.com/ee/user/packages/container_registry/

## GitLab Container Registry
The GitLab Container Registry is a secure, private registry for Docker and OCI container images built directly into GitLab.

### Authenticating & Pushing Container Images
To authenticate and push images within a CI/CD job using predefined variables:
```yaml
build_docker_image:
  image: docker:24.0.5
  services:
    - docker:24.0.5-dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

To authenticate from a local workstation:
```bash
docker login registry.gitlab.com -u <your_username> -p <your_personal_access_token>
docker tag my-local-image:latest registry.gitlab.com/my-group/my-project:v1.0
docker push registry.gitlab.com/my-group/my-project:v1.0
```

## GitLab Package Registry
GitLab includes a built-in Package Registry supporting major package managers:
- **npm**: Publish and install private Node.js packages using `@scope:registry=https://gitlab.com/api/v4/packages/npm/`.
- **PyPI**: Publish Python packages using `twine upload --repository-url https://gitlab.com/api/v4/projects/<project_id>/packages/pypi dist/*`.
- **Maven**: Publish Java artifacts via Maven/Gradle.
- **Generic Packages**: Upload arbitrary binary files or release assets via HTTP PUT.
  ```bash
  curl --header "PRIVATE-TOKEN: <access_token>" \
    --upload-file my-app-v1.0.tar.gz \
    "https://gitlab.com/api/v4/projects/12345/packages/generic/my-app/1.0.0/my-app-v1.0.tar.gz"
  ```
