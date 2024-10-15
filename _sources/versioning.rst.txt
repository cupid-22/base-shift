==============================
Versioning
==============================

This section details the versioning strategy for the project, ensuring consistency and clarity in releases.

**Versioning Scheme:**

1. **Semantic Versioning (SemVer):**
   - The project follows the Semantic Versioning 2.0.0 standard.
   - Version numbers are in the format `MAJOR.MINOR.PATCH`.

2. **Version Components:**
   - **MAJOR:** Increments when there are incompatible API changes.
   - **MINOR:** Increments when new functionality is added in a backward-compatible manner.
   - **PATCH:** Increments when backward-compatible bug fixes are made.

**Releasing a New Version:**

1. **Release Preparation:**
   - Ensure all features and fixes intended for the release are merged into the `main` branch.
   - Update the `CHANGELOG.rst` with the list of changes in the new version.
   - Update the version number in the relevant configuration files.

2. **Tagging the Release:**
   - Create a new Git tag for the release:
     ```
     git tag -a vX.Y.Z -m "Release X.Y.Z"
     ```
   - Push the tags to the remote repository:
     ```
     git push origin --tags
     ```

3. **Building and Deployment:**
   - Build the project using the CI/CD pipeline.
   - Deploy the new version to the staging environment for final testing.
   - After successful testing, deploy to the production environment.

**Maintaining Older Versions:**

1. **LTS (Long-Term Support) Releases:**
   - Designate certain versions as LTS to receive extended support and critical bug fixes.
   - Backport critical fixes from the `main` branch to the LTS branch as needed.

2. **Patch Releases:**
   - For non-LTS versions, release patches as necessary to address critical bugs or security issues.
   - Ensure patch versions do not introduce new features or break existing functionality.

**Version Compatibility:**

1. **API Compatibility:**
   - Maintain backward compatibility within a major version whenever possible.
   - Deprecate features with clear warnings before removal in a future major version.

2. **Database Schema:**
   - Handle database schema changes with care, ensuring migrations are backward-compatible within a minor version.
   - Use tools like Alembic (for Python) or Liquibase (for JavaScript) for managing migrations.

3. **Dependency Management:**
   - Regularly update dependencies to maintain compatibility and security.
   - Document any required changes in the `setup_tools.rst` when upgrading dependencies.

**References:**

- `Semantic Versioning 2.0.0 <https://semver.org/>`_
- `Git Tagging Documentation <https://git-scm.com/book/en/v2/Git-Basics-Tagging>`_
- `Alembic Documentation <https://alembic.sqlalchemy.org/en/latest/>`_
