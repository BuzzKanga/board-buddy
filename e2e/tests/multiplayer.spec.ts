import { test, expect } from '@playwright/test';

test.describe('Multiplayer Kanban', () => {
  test('users see real-time updates across sessions', async ({ browser }) => {
    // Session 1: User 1 creates the board and card
    const context1 = await browser.newContext();
    const page1 = await context1.newPage();
    
    await page1.goto('/');
    
    // Fill identity gate
    await page1.fill('#identity-name', 'user1');
    await page1.getByRole('button', { name: 'Save' }).click();
    
    // Create board
    await page1.getByPlaceholder('New board name…').fill('board1');
    await page1.getByRole('button', { name: 'Create board' }).click();
    
    // Wait to navigate to the board page
    await page1.waitForURL(/\/boards\/.+/);
    const boardUrl = page1.url();
    
    // Check that default columns exist
    await expect(page1.getByRole('heading', { name: 'To Do' })).toBeVisible();
    
    // Add a card in the "To Do" column
    const todoColumn = page1.locator('section').filter({ hasText: 'To Do' });
    await todoColumn.getByRole('button', { name: 'Add a card' }).click();
    await todoColumn.getByPlaceholder('Card title').fill('Card 1');
    await todoColumn.getByRole('button', { name: 'Add card', exact: true }).click();
    
    // Verify card is created
    await expect(todoColumn.getByText('Card 1')).toBeVisible();

    // Session 2: User 2 joins the board
    const context2 = await browser.newContext();
    const page2 = await context2.newPage();
    
    await page2.goto(boardUrl);
    
    // Fill identity gate for User 2
    await page2.fill('#identity-name', 'user2');
    await page2.getByRole('button', { name: 'Save' }).click();
    
    // Verify User 2 sees the card
    const todoColumn2 = page2.locator('section').filter({ hasText: 'To Do' });
    await expect(todoColumn2.getByText('Card 1')).toBeVisible();
    
    // User 2 edits the card title
    await todoColumn2.getByText('Card 1').click();
    await expect(page2.getByRole('heading', { name: 'Card details' })).toBeVisible();
    await page2.fill('#card-title', 'Card 1 updated');
    await page2.getByRole('button', { name: 'Save changes' }).click();
    
    // Verify User 2 sees the updated card
    await expect(todoColumn2.getByText('Card 1 updated')).toBeVisible();
    
    // Verify User 1 sees the updated card in real-time (without refresh)
    const todoColumn1 = page1.locator('section').filter({ hasText: 'To Do' });
    await expect(todoColumn1.getByText('Card 1 updated')).toBeVisible();
  });
});
