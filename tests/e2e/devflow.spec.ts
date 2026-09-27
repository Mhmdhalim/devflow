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


test("organization invitation works end to end", async ({ page, browser, baseURL }) => {
  const runId = Date.now().toString();
  const ownerEmail = `owner+${runId}@example.com`;
  const memberEmail = `member+${runId}@example.com`;
  const workspaceName = `Invite Workspace ${runId}`;
  const workspaceSlug = `invite-workspace-${runId}`;
  const projectName = `Shared Project ${runId}`;
  const projectKey = `SHR${runId.slice(-6)}`;

  await page.goto("/register");
  await page.getByLabel("Full name").fill("Invitation Owner");
  await page.getByLabel("Email address").fill(ownerEmail);
  await page.getByLabel("Password").fill("password123");
  await page.getByRole("button", { name: "Create account" }).click();

  await page.getByRole("button", { name: "+ New workspace" }).click();
  const workspaceDialog = page.getByRole("dialog", { name: "New workspace" });
  await workspaceDialog.getByLabel("Name").fill(workspaceName);
  await workspaceDialog.getByLabel("Slug").fill(workspaceSlug);
  await workspaceDialog.getByRole("button", { name: "Create workspace" }).click();

  await page.getByRole("button", { name: "+ Project" }).click();
  const projectDialog = page.getByRole("dialog", { name: "New project" });
  await projectDialog.getByLabel("Project name").fill(projectName);
  await projectDialog.getByLabel("Key").fill(projectKey);
  await projectDialog.getByRole("button", { name: "Create project" }).click();

  const sharedProjectLink = page.getByRole("link", { name: new RegExp(projectName) });
  const projectHref = await sharedProjectLink.getAttribute("href");
  expect(projectHref).toBeTruthy();

  await page.getByRole("link", { name: "Members" }).click();
  await page.getByLabel("Email address").fill(memberEmail);
  await page.getByLabel("Role").selectOption("member");
  await page.getByRole("button", { name: "Create invite" }).click();

  const inviteUrl = await page.locator(".invite-link-row input").inputValue();
  expect(inviteUrl).toContain("/invite/");

  const memberContext = await browser.newContext({ baseURL });
  const memberPage = await memberContext.newPage();

  await memberPage.goto(inviteUrl);
  await expect(
    memberPage.getByRole("heading", { name: "Sign in to DevFlow" }),
  ).toBeVisible();

  await memberPage.getByRole("link", { name: "Create an account" }).click();
  await memberPage.getByLabel("Full name").fill("Invited Member");
  await memberPage.getByLabel("Email address").fill(memberEmail);
  await memberPage.getByLabel("Password").fill("password123");
  await memberPage.getByRole("button", { name: "Create account" }).click();

  await expect(
    memberPage.getByRole("heading", { name: "Workspace invitation" }),
  ).toBeVisible();
  await expect(memberPage.getByRole("heading", { name: workspaceName })).toBeVisible();
  await memberPage.getByRole("button", { name: "Accept invitation" }).click();

  await expect(memberPage.getByRole("heading", { name: "Workspaces" })).toBeVisible();
  await expect(memberPage.getByRole("heading", { name: workspaceName })).toBeVisible();
  await expect(
    memberPage.getByRole("link", { name: new RegExp(projectName) }),
  ).toBeVisible();

  await page.reload();
  await expect(page.getByText(memberEmail)).toBeVisible();

  await memberContext.close();

  const outsiderContext = await browser.newContext({ baseURL });
  const outsiderPage = await outsiderContext.newPage();

  await outsiderPage.goto("/register");
  await outsiderPage.getByLabel("Full name").fill("Outside User");
  await outsiderPage.getByLabel("Email address").fill(`outsider+${runId}@example.com`);
  await outsiderPage.getByLabel("Password").fill("password123");
  await outsiderPage.getByRole("button", { name: "Create account" }).click();

  await expect(outsiderPage.getByRole("heading", { name: workspaceName })).toHaveCount(0);
  await outsiderPage.goto(projectHref!);
  await expect(outsiderPage.getByText("Unable to load this project")).toBeVisible();

  await outsiderContext.close();
});


test("invited user sees pending invitation after normal sign in", async ({ page, browser, baseURL }) => {
  const runId = Date.now().toString();
  const ownerEmail = `inbox-owner+${runId}@example.com`;
  const memberEmail = `inbox-member+${runId}@example.com`;
  const workspaceName = `Inbox Workspace ${runId}`;
  const workspaceSlug = `inbox-workspace-${runId}`;

  await page.goto("/register");
  await page.getByLabel("Full name").fill("Inbox Owner");
  await page.getByLabel("Email address").fill(ownerEmail);
  await page.getByLabel("Password").fill("password123");
  await page.getByRole("button", { name: "Create account" }).click();

  await page.getByRole("button", { name: "+ New workspace" }).click();
  const workspaceDialog = page.getByRole("dialog", { name: "New workspace" });
  await workspaceDialog.getByLabel("Name").fill(workspaceName);
  await workspaceDialog.getByLabel("Slug").fill(workspaceSlug);
  await workspaceDialog.getByRole("button", { name: "Create workspace" }).click();

  await page.getByRole("link", { name: "Members" }).click();
  await page.getByLabel("Email address").fill(memberEmail);
  await page.getByLabel("Role").selectOption("member");
  await page.getByRole("button", { name: "Create invite" }).click();

  const memberContext = await browser.newContext({ baseURL });
  const memberPage = await memberContext.newPage();

  await memberPage.goto("/register");
  await memberPage.getByLabel("Full name").fill("Inbox Member");
  await memberPage.getByLabel("Email address").fill(memberEmail);
  await memberPage.getByLabel("Password").fill("password123");
  await memberPage.getByRole("button", { name: "Create account" }).click();

  const inbox = memberPage.getByRole("region", { name: "Pending invitations" });
  await expect(inbox).toBeVisible();
  await expect(inbox.getByText(workspaceName)).toBeVisible();
  await inbox.getByRole("button", { name: "Accept" }).click();

  await expect(inbox).not.toBeVisible();
  await expect(memberPage.getByRole("heading", { name: workspaceName })).toBeVisible();

  await memberContext.close();
});
