package imagefinder

import (
	"context"
	"fmt"
	"log"
	"strings"

	"image-updater/internal/github"
)

type ImageFinder struct {
	ghClient *github.Client

	deprecatedImages []string
}

func New(ghClient *github.Client, deprecatedImages []string) *ImageFinder {
	return &ImageFinder{
		ghClient:         ghClient,
		deprecatedImages: deprecatedImages,
	}
}

func (f *ImageFinder) FindDeprecated(ctx context.Context, org string) (map[string][]string, error) {
	repos, err := f.ghClient.ListRepositories(ctx, org)
	if err != nil {
		return nil, fmt.Errorf("error fetching repositories: %v", err)
	}

	results := make(map[string][]string)
	for _, repo := range repos {
		content, err := f.ghClient.GetFileContent(ctx, org, *repo.Name, ".circleci/config.yml")
		if err != nil && strings.Contains(err.Error(), "404") {
			log.Printf("No .circleci/config.yml found in %s", *repo.Name)
			continue
		}
		if err != nil {
			log.Printf("Error getting file content: %v", err)
			continue
		}

		var foundDeprecatedImages []string
		for _, image := range f.deprecatedImages {
			if strings.Contains(content, image) {
				foundDeprecatedImages = append(foundDeprecatedImages, image)
			}
		}

		if len(foundDeprecatedImages) > 0 {
			results[*repo.Name] = foundDeprecatedImages
			log.Printf("Repository Name: %s, Images to Update: %s", *repo.Name, strings.Join(foundDeprecatedImages, ","))
		}
	}
	return results, nil
}
