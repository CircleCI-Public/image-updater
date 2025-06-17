package main

import (
	"context"
	"log"
	"os"
	"slices"
	"testing"

	"image-updater/internal/github"
	"image-updater/internal/imagefinder"
	"image-updater/internal/testing/fakegithub"

	"github.com/stretchr/testify/assert"
)

func TestMain(t *testing.T) {
	// Setup test environment
	ctx := context.Background()
	server := fakegithub.Service()
	defer server.Close()

	// Set required environment variable
	os.Setenv("GITHUB_TOKEN", "fake-token")
	t.Cleanup(func() { os.Unsetenv("GITHUB_TOKEN") })

	// Create client pointing to fake server
	client, err := github.NewClient(ctx, server.URL+"/", "fake-token")
	assert.NoError(t, err)

	// Test with test organization
	imgFinder := imagefinder.New(client, slices.Concat(linuxImages, dockerImages))
	_, err = imgFinder.FindDeprecated(ctx, "testorg")
	assert.NoError(t, err)
}

func TestMainValidation_GitHubTokenMissing(t *testing.T) {
	// Ensure GITHUB_TOKEN is not set
	os.Unsetenv("GITHUB_TOKEN")
	t.Cleanup(func() { os.Unsetenv("GITHUB_TOKEN") })

	oldArgs := os.Args
	t.Cleanup(func() { os.Args = oldArgs })

	// Simulate command line arguments
	os.Args = []string{"cmd", "-org", "testorg"}

	// Capture log output
	log.SetOutput(os.Stdout)
	t.Cleanup(func() { log.SetOutput(os.Stderr) })

	// Test should fail due to missing token
	assert.Panics(t, func() {
		main()
	})
}

func TestMainValidation_OrgMissing(t *testing.T) {
	// Set required environment variable
	os.Setenv("GITHUB_TOKEN", "fake-token")
	t.Cleanup(func() { os.Unsetenv("GITHUB_TOKEN") })

	oldArgs := os.Args
	t.Cleanup(func() { os.Args = oldArgs })

	// Simulate command line arguments without org flag
	os.Args = []string{"cmd"}

	// Capture log output
	log.SetOutput(os.Stdout)
	t.Cleanup(func() { log.SetOutput(os.Stderr) })

	// Test should fail due to missing org flag
	assert.Panics(t, func() {
		main()
	})
}
