Use the commit-code-reviewer agent to review the code and provide structured feedback.

The target to review is: $ARGUMENTS

If $ARGUMENTS is empty, review the most recent git commit.
If $ARGUMENTS is a file or folder path, focus the review on that specific file or folder.
If $ARGUMENTS describes a task or feature, focus the review on code relevant to that task.

Invoke the commit-code-reviewer agent and report its findings back to the user.
