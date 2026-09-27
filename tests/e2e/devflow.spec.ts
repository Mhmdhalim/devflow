import { expect, test } from "@playwright/test";

test("full DevFlow workflow works end to end", async ({ page }) => {
  const runId = Date.now().toString();
  const email = `e2e+${runId}@example.com`;
  const workspaceName = `E2E Workspace ${runId}`;
  const workspaceSlug = `e2e-workspace-${runId}`;
  const projectName = `E2E Project ${runId}`;
  const projectKey = `E2E${runId.slice(-6)}`;
  const issueTitle = `End-to-end issue ${runId}`;
  const commentBody = `E2E comment ${runId}`;
  const labelName = `e2e-${runId.slice(-6)}`;

  await page.goto("/register");

  await page.getByLabel("Full name").fill("E2E Test User");
  await page.getByLabel("Email address").fill(email);
  await page.getByLabel("Password").fill("password123");
  await page.getByRole("button", { name: "Create account" }).click();

  await expect(page.getByRole("heading", { name: "Workspaces" })).toBeVisible();

  await page.getByRole("button", { name: "+ New workspace" }).click();
  const workspaceDialog = page.getByRole("dialog", { name: "New workspace" });
  await workspaceDialog.getByLabel("Name").fill(workspaceName);
  await workspaceDialog.getByLabel("Slug").fill(workspaceSlug);
  await workspaceDialog.getByRole("button", { name: "Create workspace" }).click();

  await expect(page.getByRole("heading", { name: workspaceName })).toBeVisible();

  await page.getByRole("button", { name: "+ Project" }).click();
  const projectDialog = page.getByRole("dialog", { name: "New project" });
  await projectDialog.getByLabel("Project name").fill(projectName);
  await projectDialog.getByLabel("Key").fill(projectKey);
  await projectDialog.getByRole("button", { name: "Create project" }).click();

  const projectLink = page.getByRole("link", { name: new RegExp(projectName) });
  await expect(projectLink).toBeVisible();
  await projectLink.click();

  await expect(page.getByRole("heading", { name: projectName })).toBeVisible();

  await page.getByRole("button", { name: "+ New issue" }).click();
  const issueDialog = page.getByRole("dialog", { name: "Create issue" });
  await issueDialog.getByLabel("Title").fill(issueTitle);
  await issueDialog.getByLabel("Description optional").fill("Created by the full-stack E2E smoke test.");
  await issueDialog.getByLabel("Priority").selectOption("high");
  await issueDialog.getByRole("button", { name: "Create issue" }).click();

  await expect(page.getByText(issueTitle)).toBeVisible();
  await page.getByText(issueTitle).click();

  const detailDialog = page.getByRole("dialog", { name: new RegExp(issueTitle) });
  await detailDialog.getByLabel("Status").selectOption("in_progress");
  await detailDialog.getByRole("button", { name: "Save changes" }).click();
  await expect(detailDialog.getByLabel("Status")).toHaveValue("in_progress");

  await detailDialog.getByPlaceholder("Add a comment…").fill(commentBody);
  await detailDialog.getByRole("button", { name: "Comment" }).click();
  await expect(detailDialog.getByText(commentBody)).toBeVisible();

  await detailDialog.getByRole("button", { name: "Close dialog" }).click();

  await page.getByRole("button", { name: "+ Label" }).click();
  const labelDialog = page.getByRole("dialog", { name: "Create label" });
  await labelDialog.getByLabel("Name").fill(labelName);
  await labelDialog.getByRole("button", { name: "Create label" }).click();

  await page.getByText(issueTitle).click();
  const reopenedDialog = page.getByRole("dialog", { name: new RegExp(issueTitle) });
  const labelButton = reopenedDialog.getByRole("button", { name: labelName });
  await labelButton.click();
  await expect(reopenedDialog.getByRole("button", { name: new RegExp(`${labelName}.*✓`) })).toBeVisible();

  await reopenedDialog.getByRole("button", { name: "Close dialog" }).click();

  await page.getByLabel("Filter by label").selectOption({ label: labelName });
  await expect(page.getByText(issueTitle)).toBeVisible();
});
