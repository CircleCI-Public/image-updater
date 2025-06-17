package fakegithub

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
)

// Service creates a test server that mimics GitHub API responses
func Service() *httptest.Server {
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/orgs/testorg/repos":
			repos := []map[string]any{
				{
					"name":     "repo1",
					"html_url": "https://github.com/testorg/repo1",
				},
				{
					"name":     "repo2",
					"html_url": "https://github.com/testorg/repo2",
				},
			}
			err := json.NewEncoder(w).Encode(repos)
			if err != nil {
				panic(err)
			}
		case "/repos/testorg/repo1/contents/.circleci/config.yml":
			content := map[string]any{
				"content": "image: ubuntu-2204:2024.02.7\n image: deprecated-image:1.0",
			}
			err := json.NewEncoder(w).Encode(content)
			if err != nil {
				panic(err)
			}
		case "/repos/testorg/repo2/contents/.circleci/config.yml":
			content := map[string]any{
				"content": "image: android:2024.4.5",
			}
			err := json.NewEncoder(w).Encode(content)
			if err != nil {
				panic(err)
			}
		default:
			w.WriteHeader(http.StatusNotFound)
		}
	}))
}
