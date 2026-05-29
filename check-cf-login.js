const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    headless: false,
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
  });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('导航到 https://dash.cloudflare.com ...');
  await page.goto('https://dash.cloudflare.com', { waitUntil: 'networkidle', timeout: 60000 });

  // 等待页面稳定
  await page.waitForTimeout(3000);

  const url = page.url();
  const title = await page.title();
  console.log('当前URL:', url);
  console.log('页面标题:', title);

  // 检查登录状态的特征
  const hasLoginForm = await page.locator('input[type="email"]').count() > 0;
  const hasPasswordField = await page.locator('input[type="password"]').count() > 0;
  const hasDashboardContent = await page.locator('text=Dashboard').count() > 0 || await page.locator('text=Overview').count() > 0;
  const hasUserAvatar = await page.locator('img[alt*="avatar"], [data-testid*="avatar"], .avatar').count() > 0;

  console.log('\n--- 登录状态检测结果 ---');
  console.log('页面有邮箱输入框:', hasLoginForm);
  console.log('页面有密码输入框:', hasPasswordField);
  console.log('页面有Dashboard内容:', hasDashboardContent);
  console.log('页面有用户头像:', hasUserAvatar);

  if (hasLoginForm || hasPasswordField) {
    console.log('\n结论: 未登录 - 页面显示登录表单');
  } else if (hasDashboardContent || hasUserAvatar) {
    console.log('\n结论: 已登录 - 页面显示Dashboard内容');
  } else {
    console.log('\n结论: 状态不明，需要人工确认');
  }

  // 截图
  const screenshotPath = 'E:\\traework\\000 做网站赚钱\\cf-login-status.png';
  await page.screenshot({ path: screenshotPath, fullPage: true });
  console.log('\n截图已保存到:', screenshotPath);

  // 保持浏览器打开一段时间供查看
  console.log('浏览器将在30秒后关闭...');
  await page.waitForTimeout(30000);

  await browser.close();
})();
