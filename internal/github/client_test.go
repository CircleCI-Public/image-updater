package github

import (
	"context"
	"testing"

	"gotest.tools/v3/assert/cmp"

	"image-updater/internal/testing/fakegithub"

	"gotest.tools/v3/assert"
)

func TestClient(t *testing.T) {
	ctx := context.Background()

	server := fakegithub.Service()
	defer server.Close()

	client, err := NewClient(ctx, server.URL+"/", "fake-token")
	assert.NilError(t, err)

	t.Run("ListRepositories", func(t *testing.T) {
		repos, err := client.ListRepositories(ctx, "testorg")
		assert.NilError(t, err)
		assert.Check(t, cmp.Len(repos, 2))
		assert.Equal(t, "repo1", *repos[0].Name)
		assert.Equal(t, "repo2", *repos[1].Name)
	})

	t.Run("GetFileContent", func(t *testing.T) {
		content, err := client.GetFileContent(ctx, "testorg", "repo1", ".circleci/config.yml")
		assert.NilError(t, err)
		assert.Check(t, cmp.Contains(content, "ubuntu-2204:2024.02.7"))

		_, err = client.GetFileContent(ctx, "testorg", "reponotfound", ".circleci/config.yml")
		assert.Check(t, cmp.ErrorIs(err, ErrNotFound))
	})
}
