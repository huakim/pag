import re

import bs4

import fedora.client

from pag.utils import repo_url


class PagureException(Exception):
    pass


class Pagure(fedora.client.OpenIdBaseClient):
    def __init__(self, url='https://pagure.io', insecure=False):
        super(Pagure, self).__init__(
            base_url=url,
            login_url=url + "/login/",
            useragent="pag (cli)",
            debug=False,
            insecure=insecure,
            openid_insecure=insecure,
            username=None,  # We supply this later
            cache_session=True,
            retries=7,
            timeout=120,
            retry_backoff_factor=0.3,
        )

    @property
    def is_logged_in(self):
        response = self._session.get(self.base_url)
        return "logout" in response.text

    def _get_csrf_token(self, url):
        response = self._session.get(url)
        if not bool(response):
            raise PagureException("Couldn't get form to get "
                                  "csrf token %r" % response)

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        return soup.find(id='csrf_token').attrs['value']

    def _post(self, url, data, action=''):
        response = self._session.post(url, data=data)

        if not bool(response):
            del data['csrf_token']
            raise PagureException('Bad status code from pagure when '
                                  '%s: %r.  Sent %r' % (
                                      action, response, data))
        return response

    def create(self, name, description):
        if not self.is_logged_in:
            raise PagureException('Not logged in.')
        url = self.base_url + '/new'
        data = dict(
            csrf_token=self._get_csrf_token(url),
            name=name,
            description=description,
        )

        self._post(url, data=data, action='creating project')
        return repo_url(name)

    def create_issue(self, repo, title, description, private=False):
        if not self.is_logged_in:
            raise PagureException('Not logged in.')

        url = self.base_url + '/' + repo + '/new_issue'
        data = {
            'csrf_token': self._get_csrf_token(url),
            'title': title,
            'issue_content': description,
            'private': private
        }

        response = self._post(url, data=data, action='creating issue')

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        response_title = soup.title.string
        match = re.match(r'Issue #(?P<issue_id>\d+):.*', response_title)
        issue_id = match.group('issue_id')
        issue_url = self.base_url + '/' + repo + '/issue/' + issue_id
        return issue_url

    def upload(self, repo, filepath):
        if not self.is_logged_in:
            raise PagureException('Not logged in.')

        url = self.base_url + '/' + repo + '/upload'
        data = {
            'csrf_token': self._get_csrf_token(url),
        }
        files = {
            'filestream': open(filepath, 'rb')
        }
        response = self._session.post(url, data=data, files=files)
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        alert = soup.find(class_="alert")
        if 'alert-info' in alert.attrs['class']:
            # Not an error -> the upload was successful.
            return None
        # Filter out only text elements from the alert (throwing away the close
        # button).
        text = ''.join(str(c) for c in alert.children
                       if isinstance(c, bs4.element.NavigableString))
        return text.strip()

    def fork(self, name):
        if not self.is_logged_in:
            raise PagureException('Not logged in.')

        url = self.base_url + '/' + name
        data = dict(
            csrf_token=self._get_csrf_token(url),
        )

        url = self.base_url + '/do_fork/' + name
        self._post(url, data=data, action='forking project')
        return repo_url(name)

    def submit_pull_request(self, name, base, head, title, comment):
        url = self.base_url + '/{name}/diff/{base}..{head}'
        url = url.format(name=name, base=base, head=head)

        data = dict(
            csrf_token=self._get_csrf_token(url),
            branch_to=base,
            title=title,
            initial_comment=comment,
        )
        response = self._post(url, data=data, action='creating pull request')
        return response.url


client = Pagure()
