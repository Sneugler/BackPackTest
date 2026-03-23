# Example Usage

```bash
aegisforge doctor
aegisforge project bootstrap examples/authorization/project.yaml examples/scope/targets.yaml
aegisforge project summary
aegisforge audit secrets examples/code
aegisforge audit dependencies examples/code
aegisforge api review examples/scope/openapi.yaml
aegisforge automate plan <project-id>
aegisforge operator findings <project-id>
aegisforge operator toolkit <project-id>
aegisforge operator preflight <project-id> "app.example.com" "configuration review,network scanning"
aegisforge operator export-toolkit <project-id>
aegisforge operator campaign <project-id>
aegisforge evidence search <project-id> http
aegisforge report pack <project-id>
aegisforge report build <project-id>
```

Dashboard views:
- `/` portfolio GUI
- `/projects/<project-id>/dashboard` project GUI
- `/projects/<project-id>/campaign` campaign JSON view
