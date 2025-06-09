package imagefinder

import (
	"context"
	"testing"

	"image-updater/internal/github"
	"image-updater/internal/testing/fakegithub"

	"github.com/stretchr/testify/assert"
)

func TestFindDeprecated_Integration(t *testing.T) {
	ctx := context.Background()

	server := fakegithub.Service()
	defer server.Close()

	client, err := github.NewClient(ctx, server.URL+"/", "fake-token")
	assert.NoError(t, err)

	finder := New(client, []string{"ubuntu-2204:2024.02.7", "deprecated-image:1.0", "android:2024.4.5"})

	results, err := finder.FindDeprecated(ctx, "testorg")
	assert.NoError(t, err)
	assert.Equal(t, results, map[string][]string{
		"repo1": {"ubuntu-2204:2024.02.7", "deprecated-image:1.0"},
		"repo2": {"android:2024.4.5"},
	})
}
