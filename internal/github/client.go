package github

import (
	"context"
	"fmt"
	"net/http"
	"net/url"

	"github.com/google/go-github/v60/github"
	"golang.org/x/oauth2"
)

var (
	ErrNotFound  = fmt.Errorf("not found")
	ErrForbidden = fmt.Errorf("forbidden")
)

type Client struct {
	client *github.Client
}

func NewClient(ctx context.Context, baseURL, token string) (_ *Client, err error) {
	tc := oauth2.NewClient(ctx, oauth2.StaticTokenSource(
		&oauth2.Token{
			AccessToken: token,
		}),
	)

	cl := github.NewClient(tc)

	// Only used to override the base URL for testing
	if baseURL != "" {
		cl.BaseURL, err = url.Parse(baseURL)
		if err != nil {
			return nil, fmt.Errorf("error parsing base URL: %v", err)
		}
	}

	return &Client{
		client: cl,
	}, nil
}

// ListRepositories fetches all repositories for an organization
func (c *Client) ListRepositories(ctx context.Context, org string) ([]*github.Repository, error) {
	var allRepos []*github.Repository
	opts := &github.RepositoryListByOrgOptions{
		Type:        "all",
		ListOptions: github.ListOptions{PerPage: 100},
	}

	for {
		repos, resp, err := c.client.Repositories.ListByOrg(ctx, org, opts)
		if err != nil {
			return nil, fmt.Errorf("error listing repositories: %v", statusCodeToError(resp, err))
		}
		allRepos = append(allRepos, repos...)

		if resp.NextPage == 0 {
			break
		}
		opts.Page = resp.NextPage
	}

	return allRepos, nil
}

// GetFileContent fetches the content of a file from a repository
func (c *Client) GetFileContent(ctx context.Context, org, repo, path string) (string, error) {
	content, _, resp, err := c.client.Repositories.GetContents(ctx, org, repo, path, nil)
	if err != nil {
		return "", statusCodeToError(resp, err)
	}

	decoded, err := content.GetContent()
	if err != nil {
		return "", err
	}

	return decoded, nil
}

func statusCodeToError(resp *github.Response, err error) error {
	if resp == nil {
		return err
	}

	switch resp.StatusCode {
	case http.StatusForbidden:
		return fmt.Errorf("%w: %s", ErrForbidden, err)
	case http.StatusNotFound:
		return fmt.Errorf("%w: %s", ErrNotFound, err)
	}
	return err
}
