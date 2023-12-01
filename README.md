<h1 align="center">
  cnb-tools
</h1>

<h3 align="center">
  Convenience tools/functions for challenges and benchmarking on
  <a href="https://www.synapse.org" title="Synapse.org">Synapse.org</a>
</h3>
<br/>

<p align="center">
  <img alt="PyPI version" src="https://img.shields.io/badge/pypi-1 | Planning-%23679EC1?style=flat-square&logo=pypi&logoColor=white">
  <img alt="Supported Python versions" src="https://img.shields.io/badge/python-3.9 | 3.10 | 3.11 | 3.12-%23EB8231?style=flat-square&logo=python&logoColor=white">
  <img alt="License" src="https://img.shields.io/github/license/Sage-Bionetworks-Challenges/cnb-tools?style=flat-square&logo=github&color=%236DB56D">
</p>

---

**Documentation**: [https://sage-bionetworks-challenges.github.io/cnb-tools]

**Source code**: [https://github.com/Sage-Bionetworks-Challenges/cnb-tools]

---

**cnb-tools** is a set of tools and commands that provides an interface
for managing crowd-sourced challenges hosted on Synapse.org, including
but not limited to, [DREAM Challenges].

## Requirements

- [Python 3.9+]
- [Synapse account]

To fully utilize **cnb-tools**, you must have a Synapse account and
provide your credentials to the tool.  To do so, create a `.synapseConfig`
file in your home directory, with the following structure:

```yaml
[authentication]
authtoken = "YOUR PAT"
```

Generate a Synapse [Personal Access Token (PAT)] with all token
permissions selected and copy-paste the token into `authtoken`.

## Installation

```
$ pip install cnb-tools
```

Verify the installation with:

```
$ cnb-tools --version
cnb-tools v0.1.0
```

## License

**cnb-tools** is released under the Apache 2.0 license.

[https://sage-bionetworks-challenges.github.io/cnb-tools]: https://sage-bionetworks-challenges.github.io/cnb-tools
[https://github.com/Sage-Bionetworks-Challenges/cnb-tools]: https://github.com/Sage-Bionetworks-Challenges/cnb-tools
[DREAM Challenges]: https://dreamchallenges.org/
[Python 3.9+]: https://www.python.org/downloads/
[Synapse account]: https://www.synapse.org/#!LoginPlace:0
[Personal Access Token (PAT)]: https://www.synapse.org/#!PersonalAccessTokens:
