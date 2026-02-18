package release

import (
	"fmt"
	"os/exec"
	"strings"
)

type GitManager struct {
	repoPath string
	logger   *ReleaseLogger
}

type GitCommit struct {
	Hash    string
	Message string
	Author  string
	Date    string
}

type GitDiff struct {
	Files        []FileChange
	AddedLines   int
	DeletedLines int
}

func NewGitManager(repoPath string, logger *ReleaseLogger) *GitManager {
	return &GitManager{
		repoPath: repoPath,
		logger:   logger,
	}
}

func (g *GitManager) GetLatestTag() (string, error) {
	cmd := exec.Command("git", "describe", "--tags", "--abbrev=0")
	cmd.Dir = g.repoPath
	output, err := cmd.Output()
	if err != nil {
		return "", fmt.Errorf("failed to get latest tag: %w", err)
	}
	return strings.TrimSpace(string(output)), nil
}

func (g *GitManager) GetCurrentBranch() (string, error) {
	cmd := exec.Command("git", "rev-parse", "--abbrev-ref", "HEAD")
	cmd.Dir = g.repoPath
	output, err := cmd.Output()
	if err != nil {
		return "", fmt.Errorf("failed to get current branch: %w", err)
	}
	return strings.TrimSpace(string(output)), nil
}

func (g *GitManager) GetCommitsSinceTag(tag string) ([]GitCommit, error) {
	cmd := exec.Command("git", "log", fmt.Sprintf("%s..HEAD", tag), "--pretty=format:%H|%s|%an|%ad", "--date=short")
	cmd.Dir = g.repoPath
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("failed to get commits: %w", err)
	}

	lines := strings.Split(strings.TrimSpace(string(output)), "\n")
	commits := make([]GitCommit, 0, len(lines))

	for _, line := range lines {
		if line == "" {
			continue
		}
		parts := strings.SplitN(line, "|", 4)
		if len(parts) >= 4 {
			commits = append(commits, GitCommit{
				Hash:    parts[0],
				Message: parts[1],
				Author:  parts[2],
				Date:    parts[3],
			})
		}
	}

	return commits, nil
}

func (g *GitManager) GetDiffSinceTag(tag string) (*GitDiff, error) {
	cmd := exec.Command("git", "diff", fmt.Sprintf("%s..HEAD", tag), "--numstat")
	cmd.Dir = g.repoPath
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("failed to get diff: %w", err)
	}

	diff := &GitDiff{
		Files: make([]FileChange, 0),
	}

	lines := strings.Split(strings.TrimSpace(string(output)), "\n")
	for _, line := range lines {
		if line == "" {
			continue
		}
		parts := strings.Fields(line)
		if len(parts) >= 3 {
			added := 0
			deleted := 0
			fmt.Sscanf(parts[0], "%d", &added)
			fmt.Sscanf(parts[1], "%d", &deleted)

			fileChange := FileChange{
				Path:         parts[2],
				AddedLines:   added,
				DeletedLines: deleted,
				Modified:     true,
				IsNew:        parts[0] == "-",
				IsDeleted:    parts[1] == "-",
			}
			diff.Files = append(diff.Files, fileChange)
			diff.AddedLines += added
			diff.DeletedLines += deleted
		}
	}

	return diff, nil
}

func (g *GitManager) GetChangedFiles() ([]string, error) {
	cmd := exec.Command("git", "diff", "--name-only", "HEAD~1", "HEAD")
	cmd.Dir = g.repoPath
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("failed to get changed files: %w", err)
	}

	files := strings.Split(strings.TrimSpace(string(output)), "\n")
	result := make([]string, 0, len(files))
	for _, file := range files {
		if file != "" {
			result = append(result, file)
		}
	}
	return result, nil
}

func (g *GitManager) CreateTag(version string, message string) error {
	cmd := exec.Command("git", "tag", "-a", version, "-m", message)
	cmd.Dir = g.repoPath
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("failed to create tag: %w", err)
	}
	return nil
}

func (g *GitManager) PushTag(version string) error {
	cmd := exec.Command("git", "push", "origin", version)
	cmd.Dir = g.repoPath
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("failed to push tag: %w", err)
	}
	return nil
}

func (g *GitManager) UpdateVersionFile(filePath string, version string) error {
	cmd := exec.Command("git", "add", filePath)
	cmd.Dir = g.repoPath
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("failed to stage version file: %w", err)
	}

	cmd = exec.Command("git", "commit", "-m", fmt.Sprintf("chore: bump version to %s", version))
	cmd.Dir = g.repoPath
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("failed to commit version bump: %w", err)
	}

	return nil
}

func (g *GitManager) GetCommitMessages(since string) ([]string, error) {
	commits, err := g.GetCommitsSinceTag(since)
	if err != nil {
		return nil, err
	}

	messages := make([]string, len(commits))
	for i, commit := range commits {
		messages[i] = commit.Message
	}
	return messages, nil
}

func (g *GitManager) HasChanges() (bool, error) {
	cmd := exec.Command("git", "status", "--porcelain")
	cmd.Dir = g.repoPath
	output, err := cmd.Output()
	if err != nil {
		return false, fmt.Errorf("failed to check git status: %w", err)
	}
	return len(strings.TrimSpace(string(output))) > 0, nil
}

func (g *GitManager) GetRemoteURL() (string, error) {
	cmd := exec.Command("git", "remote", "get-url", "origin")
	cmd.Dir = g.repoPath
	output, err := cmd.Output()
	if err != nil {
		return "", fmt.Errorf("failed to get remote URL: %w", err)
	}
	return strings.TrimSpace(string(output)), nil
}
