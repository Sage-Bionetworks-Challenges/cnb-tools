👋 **Hi there! We're excited you're here.**

By contributing, you are agreeing that we may redistribute your work
under this [license].

### Development process

The **cnb-tools** project is tracked with issues and pull requests
(PR). To contribute, modify the project in [your own fork] and issue
a PR once you are ready for other devs to review and discuss.

Here is a typical contribution workflow:

1. **(optional) Assign issue**

    See a [bug or feature] you'd like to handle? Go ahead and assign
    yourself!  That way, no duplicated effort will be done.  This will
    also let the community that there is some activity with the
    ticket.

2. **If you're a first-time contributor:**

    Create your own copy of **cnb-tools** by clicking on **Fork** on
    the [main repository on GitHub]. Then, clone the project to your
    local machine and add the upstream repository:

    ```
    git clone https://github.com/<your-username>/cnb-tools.git
    cd cnb-tools
    git remote add upstream https://github.com/Sage-Bionetworks-Challenges/cnb-tools.git
    ```

3. **(if applicable) Sync fork with upstream**

    Navigate to your fork on GitHub and select **Sync fork** above
    the list of files.  Review the details of the upstream commits
    as needed, then click **Update branch**.

4. **Branch off `develop` and develop your contribution**

    Ensure `develop` is up-to-date in your local dev, then create
    a new feature branch. We recommend prefixing the new branch name
    with either `bug` or `feat` — depending on what you're working
    on — followed by its GH tracking number:

    ```
    git checkout develop && git pull
    git checkout -b <feat/bug-123> develop
    ```

5. **Document your changes**

    Document your contribution by adding or updating the docstrings as
    necessary. The format we follow is the [Google-style docstrings].

6. **Push changes to fork**

    If this is the first time pushing the feature branch to the fork:

    ```
    git push --set-upstream origin <feat/bug-123>
    ```

    For subsequent pushes:

    ```
    git push
    ```

7. **Open a PR to upstream `develop` once ready**

    Follow our PR template.  Someone from the Sage Challenges &
    Benchmarking team will then review, and either approve + merge
    or requests changes.

### Code style

**cnb-tool** uses [flake8] to enforce [PEP 8] styling consistency and
to check for possible errors. We recommend setting up your editor to
follow PEP 8 for a more seamless contribution experience.

### Documentation

The documentation uses [MkDocs], [mkdocstrings], and the [Material theme]. 
All docs are located in the `./docs` directory and are written in Markdown
format.

To add a new page, create a Markdown file in `./docs`, then add the page
to the `nav` setting in `./mkdocs.yml`.

To test your changes, build a local docs site that will auto-reload with
any changes:

```
mkdocs serve
```

This will serve the documentation on `http://127.0.0.1:8000`.


### Testing

!!! info "More info coming soon"


[license]: https://github.com/Sage-Bionetworks-Challenges/cnb-tools/blob/main/LICENSE
[your own fork]: https://docs.github.com/en/get-started/quickstart/fork-a-repo
[bug or feature]: https://github.com/Sage-Bionetworks-Challenges/cnb-tools/issues
[main repository on GitHub]: https://github.com/Sage-Bionetworks-Challenges/cnb-tools
[Google-style docstrings]: https://google.github.io/styleguide/pyguide.html
[flake8]: https://pypi.org/project/flake8/
[PEP 8]: https://peps.python.org/pep-0008/
[MKDocs]: https://www.mkdocs.org/
[mkdocstrings]: https://mkdocstrings.github.io/
[Material theme]: https://squidfunk.github.io/mkdocs-material/
