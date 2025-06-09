package main

import (
	"context"
	"flag"
	"os"
	"slices"

	"image-updater/internal/github"
	"image-updater/internal/imagefinder"
)

// TODO: Update with all images that will be deprecated
var linuxImages = []string{"ubuntu-2204:2024.02.7"}
var dockerImages = []string{"docker23"}

func main() {
	ctx := context.Background()

	// Get GitHub token from environment variable
	token := os.Getenv("GITHUB_TOKEN")
	if token == "" {
		panic("GITHUB_TOKEN environment variable is required")
	}

	// Parse command line arguments
	org := flag.String("org", "", "GitHub organization name")
	flag.Parse()

	if *org == "" {
		panic("Organization name is required. Use -org flag")
	}

	client, err := github.NewClient(ctx, "", token)
	if err != nil {
		panic(err)
	}

	imgFinder := imagefinder.New(client, slices.Concat(linuxImages, dockerImages))

	_, err = imgFinder.FindDeprecated(ctx, *org)
	if err != nil {
		panic(err)
	}
}
