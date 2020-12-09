# Guidelines for Contributing to Taurus

The Taurus repository uses nvie's branching model, known as [GitFlow][].

In this model, there are two long-lived branches:

- `master`: used for official releases. **Contributors should 
  not need to use it or care about it**
- `develop`: reflects the latest integrated changes for the next 
  release. This is the one that should be used as the base for 
  developing new features or fixing bugs. 

For the contributions, we use the [Fork & Pull Model][]:

1. the contributor first [forks][] the official taurus repository
2. the contributor commits changes to a branch based on the 
   `develop` branch and pushes it to the forked repository.
3. the contributor creates a [Pull Request][] against the `develop` 
   branch of the official taurus repository.
4. anybody interested may review and comment on the Pull Request, and 
   suggest changes to it (even doing Pull Requests against the Pull
   Request branch). At this point more changes can be committed on the 
   requestor's branch until the result is satisfactory.
5. once the proposed code is considered ready by an appointed taurus 
   integrator, the integrator merges the pull request into `develop`.
   
   
## Important considerations:

In general, the contributions to taurus should consider following:

- The code must comply with the [Taurus coding conventions][]

- The contributor must be clearly identified. The commit author 
  email should be valid and usable for contacting him/her.
  
- Commit messages  should follow the [commit message guidelines][]. 
  Contributions may be rejected if their commit messages are poor.
  
- The licensing terms for the contributed code must be compatible 
  with (and preferably the same as) the license chosen for the Taurus 
  project (at the time of writing this, it is the [LGPL][], 
  version 3 *or later*).

   
## Notes:
  
- These contribution guidelines are very similar but not identical to 
  those for the [GithubFlow][] workflow. Basically, most of what the 
  GitHubFlow recommends can be applied for Taurus except that the 
  role of the `master` branch in GithubFlow is done by `develop` in our 
  case. 
  
- If the contributor wants to explicitly bring the attention of some 
  specific person to the review process, [mentions][] can be used
  
- If a pull request (or a specific commit) fixes an open issue, the pull
  request (or commit) message may contain a `Fixes #N` tag (N being 
  the number of the issue) which will automatically [close the related 
  Issue][tag_issue_closing]


[gitflow]: http://nvie.com/posts/a-successful-git-branching-model/
[Fork & Pull Model]: https://en.wikipedia.org/wiki/Fork_and_pull_model
[forks]: https://help.github.com/articles/fork-a-repo/
[Pull Request]: https://help.github.com/articles/creating-a-pull-request/
[commit message guidelines]: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
[GitHubFlow]: https://guides.github.com/introduction/flow/index.html
[mentions]: https://github.com/blog/821-mention-somebody-they-re-notified
[tag_issue_closing]: https://help.github.com/articles/closing-issues-via-commit-messages/
[Taurus coding conventions]: http://taurus-scada.org/devel/coding_guide.html
[LGPL]: http://www.gnu.org/licenses/lgpl.html
