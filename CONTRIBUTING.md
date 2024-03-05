# Contribute to Label Studio SDK

Thanks for taking the time to contribute! Contributions from people like you help make [Label Studio](https://github.com/heartexlabs/label-studio) an amazing tool to use. 

This document provides guidelines for contributing code and documentation to the Label Studio Python SDK. Following these guidelines makes it easier for the maintainers to respond to your pull requests and provide timely and helpful feedback to help you finalize your requested changes.

## Types of Contributions

You can contribute to the Label Studio SDK by submitting [bug reports and feature requests](https://github.com/heartexlabs/label-studio-sdk/issues), or by writing code to fix a bug, add a new class or method to extend the SDK, or something else valuable to the community. 

We also welcome contributions to [the examples](https://github.com/heartexlabs/label-studio-sdk/tree/master/examples)! 

Please don't use the issue tracker to ask questions. Instead, join the [Label Studio Slack Community](https://slack.labelstud.io/?source=github-sdk-contrib) to get help!

If you're not sure whether an idea you have for the Label Studio SDK matches up with our planned direction, check out the [public roadmap](https://github.com/heartexlabs/label-studio/blob/master/roadmap.md) first. 

## How to Start Contributing

If you decide to work on an issue, leave a comment so that you don't duplicate work that might be in progress and to coordinate work with others. 

If you haven't opened a pull request before, check out the [GitHub documentation on pull requests](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests).

## Contributor Guidelines

We value input from each member of the community, and we ask that you follow the Label Studio [code of conduct](https://github.com/heartexlabs/label-studio/blob/master/CODE_OF_CONDUCT.md). We are a small team, but we try to respond to issues and pull requests within 2 business days. 

### Before you start
For changes that you contribute to any of the Label Studio repositories, please do the following:
- Create issues for any major changes and enhancements that you want to make. 
- Keep pull requests specific to one issue. Shorter pull requests are preferred and are easier to review. 

### Code standards
Follow these code formatting guidelines:
- Lint your Python code with [black](https://github.com/psf/black) using `--skip-string-normalization`. 
- Use single quotes for strings.
- Use comments to describe code blocks. 
- When possible, use the following conventions for your commit messages:
  - prefix with [fix] for bugfix changes
  - prefix with [ext] for feature or external-facing changes
  - prefix with [docs] for doc-only changes

### Testing
- Include unit tests when you contribute bug fixes and new features. Unit tests help prove that your code works correctly and protects against future breaking changes.
- Make sure that the code coverage checks and automatic tests for pull requests pass. 

### Pull Request naming
Use one of the following prefixes for the title of your PR:
- `fix: `
- `feat: `
- `docs: `
- `chore: `
- `ci: `
- `perf: `
- `refactor: `
- `style: `
- `test: `

### Additional questions

If you have any questions that aren't answered in these guidelines, please find us in the #contributor channel of the [Label Studio Slack Community](https://slack.labelstud.io/?source=github-sdk-contrib).