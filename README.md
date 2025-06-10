# Cobertura Pae Backend.

This repo uses commitizen and pre-commit packages in order to manage the commit messages and the changelog.

To create a new commit, please do not try to do it manually like:

```bash
git add .
git commit -m "this is a commit"
```

This is goint to be automatically rejected and you have to use:

```bash
git add .
poetry run cz commit
```

In order to create (only the first time) the change log, please run:

```bash
poetry run cz changelog --unreleased-version "v0.1.0"
```

To update the changelog, please run:

```bash
poetry run cz changelog
```