======================================
Pull Request Size Labeling Workflow
======================================

This document outlines the rationale, structure, and implementation details of the GitHub Actions workflow designed to automatically label pull requests (PRs) based on the size of changes they introduce.

Overview
--------

As our project scales, the volume and complexity of contributions will increase, making it essential to streamline the code review process. One effective way to do this is by automatically labeling PRs based on their size. This labeling provides immediate insight into the scope of a PR, enabling reviewers to prioritize and allocate their time more effectively.

The workflow described here automatically categorizes PRs into four sizes: `small`, `medium`, `large`, and `extra-large`. These categories are based on the number of lines of code (LOC) changed, which is a reasonable proxy for the complexity and review effort required.

Implementation Details
-----------------------

**Triggering Events:**
The workflow is triggered on the following pull request events:
- `opened`: When a new PR is created.
- `synchronize`: When new commits are pushed to an existing PR.
- `reopened`: When a closed PR is reopened.

These events ensure that the label is always up-to-date with the latest changes.

**Steps Involved:**

1. **Checkout Code:**
   The first step involves checking out the code from the pull request. This allows the workflow to analyze the changes introduced in the PR.

   .. code-block:: yaml

      - name: Checkout code
        uses: actions/checkout@v3

2. **Calculate Lines of Code:**
   The next step calculates the total number of lines changed in the PR. This is done using `git diff`, which compares the PR branch with the base branch (typically `main`). The result is stored as an environment variable for subsequent steps.

   .. code-block:: yaml

      - name: Calculate lines of code
        id: diff
        run: |
          LOC=$(git diff --shortstat origin/main...HEAD | awk '{print $1}')
          echo "lines_of_code=$LOC" >> $GITHUB_ENV

3. **Determine PR Size:**
   Based on the calculated LOC, the workflow determines the size category of the PR. The thresholds are as follows:

   - `small`: Less than 10 lines changed.
   - `medium`: Between 10 and 49 lines changed.
   - `large`: Between 50 and 99 lines changed.
   - `extra-large`: 100 lines or more changed.

   These thresholds are carefully chosen to balance between being overly granular and too broad.

   .. code-block:: yaml

      - name: Set PR size label
        if: env.lines_of_code != ''
        run: |
          echo "Lines of code changed: ${{ env.lines_of_code }}"

          if [ ${{ env.lines_of_code }} -lt 10 ]; then
            echo "PR size is small"
            echo "small" > size.txt
          elif [ ${{ env.lines_of_code }} -lt 50 ]; then
            echo "PR size is medium"
            echo "medium" > size.txt
          elif [ ${{ env.lines_of_code }} -lt 100 ]; then
            echo "PR size is large"
            echo "large" > size.txt
          else
            echo "PR size is extra-large"
            echo "extra-large" > size.txt
          fi
          PR_LABEL=$(cat size.txt)
          echo "pr-label=$PR_LABEL" >> $GITHUB_ENV

4. **Apply the Label:**
   Finally, the workflow applies the determined size label to the PR using the `actions-ecosystem/action-add-labels` action. This ensures that the PR is appropriately categorized in the GitHub UI, facilitating quicker and more effective review processes.

   .. code-block:: yaml

      - name: Apply label to PR
        uses: actions-ecosystem/action-add-labels@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          labels: ${{ env.pr-label }}

Benefits and Considerations
----------------------------

**Benefits:**
- **Enhanced Review Efficiency:** Reviewers can quickly gauge the size and complexity of a PR, allowing for better prioritization.
- **Automated Consistency:** Labels are applied consistently without manual intervention, reducing human error.
- **Scalability:** As the project grows, this workflow will continue to provide value by standardizing the review process.

**Considerations:**
- **Thresholds Customization:** The thresholds for PR size can be adjusted to better fit the team’s needs. Teams with different coding practices might find different thresholds more appropriate.
- **Base Branch Configuration:** Ensure that the base branch (`origin/main` in this case) is correctly configured. This may need to be adjusted depending on the branching strategy used.

Conclusion
----------

This PR size labeling workflow is a crucial component of our CI/CD pipeline, designed to improve code review efficiency and maintain high standards of code quality. By automating this task, we reduce the cognitive load on developers and allow them to focus on the content of the code rather than administrative overhead.

