import { test, expect } from '@playwright/test';

test.describe('Jarvis UI Smoke Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigera till UI
    await page.goto('http://localhost:3000');
  });

  test('should display overview page with KPI cards', async ({ page }) => {
    // Vänta på att sidan laddas
    await page.waitForLoadState('networkidle');
    
    // Kontrollera att KPI-korten visas
    await expect(page.locator('[data-testid="kpi-card"]')).toHaveCount(4);
    
    // Kontrollera att metrics laddas (även om Core är nere)
    await expect(page.locator('[data-testid="router-hits"]')).toBeVisible();
    await expect(page.locator('[data-testid="avg-latency"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-rate"]')).toBeVisible();
    await expect(page.locator('[data-testid="active-connections"]')).toBeVisible();
  });

  test('should handle Core API down gracefully', async ({ page }) => {
    // Simulera att Core API är nere
    await page.route('**/metrics', route => route.abort());
    await page.route('**/health/live', route => route.abort());
    
    // Ladda om sidan
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Kontrollera att felmeddelande visas
    await expect(page.locator('[data-testid="core-offline-banner"]')).toBeVisible();
    await expect(page.locator('text=Core API inte tillgänglig')).toBeVisible();
    
    // Kontrollera att retry-knapp finns
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
  });

  test('should display logs page with SSE events', async ({ page }) => {
    // Navigera till logs-sidan
    await page.click('[data-testid="nav-logs"]');
    await page.waitForLoadState('networkidle');
    
    // Kontrollera att logs-containern finns
    await expect(page.locator('[data-testid="logs-container"]')).toBeVisible();
    
    // Kontrollera att SSE-status visas
    await expect(page.locator('[data-testid="sse-status"]')).toBeVisible();
    
    // Kontrollera att logg-entries kan visas
    await expect(page.locator('[data-testid="log-entry"]')).toHaveCount.greaterThan(0);
  });

  test('should handle SSE connection issues', async ({ page }) => {
    // Navigera till logs-sidan
    await page.click('[data-testid="nav-logs"]');
    await page.waitForLoadState('networkidle');
    
    // Simulera SSE-anslutningsproblem
    await page.route('**/logs/stream', route => route.abort());
    
    // Vänta på att felmeddelande visas
    await expect(page.locator('[data-testid="sse-error"]')).toBeVisible();
    await expect(page.locator('text=SSE-anslutning misslyckades')).toBeVisible();
    
    // Kontrollera att reconnect-knapp finns
    await expect(page.locator('[data-testid="reconnect-button"]')).toBeVisible();
  });

  test('should display empty states correctly', async ({ page }) => {
    // Navigera till en sida som kan vara tom
    await page.click('[data-testid="nav-tools"]');
    await page.waitForLoadState('networkidle');
    
    // Kontrollera att empty state visas om inga tools finns
    const emptyState = page.locator('[data-testid="empty-state"]');
    if (await emptyState.isVisible()) {
      await expect(emptyState).toContainText('Inga verktyg tillgängliga');
      await expect(page.locator('[data-testid="add-tool-button"]')).toBeVisible();
    }
  });

  test('should handle navigation correctly', async ({ page }) => {
    // Testa alla navigationslänkar
    const navItems = [
      { testid: 'nav-overview', expectedTitle: 'Översikt' },
      { testid: 'nav-logs', expectedTitle: 'Loggar' },
      { testid: 'nav-tools', expectedTitle: 'Verktyg' },
      { testid: 'nav-settings', expectedTitle: 'Inställningar' }
    ];
    
    for (const item of navItems) {
      await page.click(`[data-testid="${item.testid}"]`);
      await page.waitForLoadState('networkidle');
      
      // Kontrollera att sidan laddades
      await expect(page.locator('h1')).toContainText(item.expectedTitle);
    }
  });

  test('should display error boundaries gracefully', async ({ page }) => {
    // Simulera ett JavaScript-fel
    await page.addInitScript(() => {
      // Simulera ett fel i komponenten
      const originalError = console.error;
      console.error = () => {}; // Tysta ner console.error
      
      // Kasta ett fel efter sidan laddats
      setTimeout(() => {
        throw new Error('Simulerat fel för testning');
      }, 100);
    });
    
    // Ladda om sidan
    await page.reload();
    await page.waitForTimeout(200);
    
    // Kontrollera att error boundary visas
    await expect(page.locator('[data-testid="error-boundary"]')).toBeVisible();
    await expect(page.locator('text=Något gick fel')).toBeVisible();
    
    // Kontrollera att retry-knapp finns
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
  });
});

test.describe('Accessibility Tests', () => {
  test('should have proper ARIA labels', async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // Kontrollera att alla interaktiva element har ARIA-labels
    await expect(page.locator('button')).toHaveAttribute('aria-label');
    await expect(page.locator('nav')).toHaveAttribute('aria-label');
    
    // Kontrollera att headings har korrekt hierarki
    const h1 = page.locator('h1');
    const h2 = page.locator('h2');
    
    await expect(h1).toHaveCount(1);
    await expect(h2).toHaveCount.greaterThan(0);
  });

  test('should support keyboard navigation', async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // Testa tab-navigation
    await page.keyboard.press('Tab');
    await expect(page.locator(':focus')).toBeVisible();
    
    // Testa enter för att aktivera knappar
    await page.keyboard.press('Enter');
    // Vänta på att något händer (sidan laddas om eller navigerar)
    await page.waitForTimeout(100);
  });
});
