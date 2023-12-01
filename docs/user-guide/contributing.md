👋 **Hi there! We're excited you're here.**

By contributing, you are agreeing that we may redistribute your work
under this [license].

### Development workflow

The **cnb-tools** project is tracked with issues and pull requests
(PR). To contribute, modify the project in [your own fork] and issue
a PR once you are ready for other devs to review and discuss.

Here is a typical contribution workflow:

1. **(optional) Self-assign issue**

    See a bug or feature you'd like to handle? Assign yourself the
    issue!  That way, no duplicated effort will be done.  This will
    also let the community that there is some activity with the
    ticket.

2. **Branch off `develop` and make changes**

    We recommend prefixing the new branch name with either `bug` or
    `feat`, depending on the issue you've assigned, followed by its
    tracking number. Also ensure `develop` is up-to-date before creating
    the new branch:

    ```
    git checkout develop && git pull
    git checkout -b <feat/bug-123> develop
    ```

3. **Push changes to fork**

    If this is the first time pushing the feature branch to the fork,
    run:

    ```
    git push --set-upstream origin <feat/bug-123>
    ```

    For subsequent pushes, run:

    ```
    git push
    ```

4. **Make a PR to `develop` once ready**

    Someone from the Sage Challenges & Benchmarking team will review,
    and will either approve + merge, or requests changes.

### Code style

**cnb-tool** uses [flake8] to enforce [PEP8] styling consistency and
to check for possible errors. We recommend verifying your code adheres
to these standards before issuing a PR.

Run **flake8** in the project root directory to check.

### Documentation

The documentation uses [MkDocs] and the [Material theme].  All docs are
located in the `./docs` directory and are written in Markdown format.

#### New pages

To add a new page, create a Markdown file in `./docs`, then add the page
to the `nav` setting in `./mkdocs.yml`.

#### Testing

During local development, you can build the docs site that will
auto-reload with any changes:

```
mkdocs serve
```

This will serve the documentation on `http://127.0.0.1:8000`.


### Testing

!!! info "More info coming soon"


[license]: LICENSE.md
[your own fork]: https://docs.github.com/en/get-started/quickstart/fork-a-repo
[flake8]: https://pypi.org/project/flake8/
[PEP8]: https://peps.python.org/pep-0008/
[MKDocs]: https://www.mkdocs.org/
[Material theme]: https://squidfunk.github.io/mkdocs-material/getting-started/
