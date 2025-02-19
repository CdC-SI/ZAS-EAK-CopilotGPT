const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const robot = require('robotjs');

async function savePageAs() {
    // Press the CMD+S or CTRL+S hotkey
    const isMac = process.platform === 'darwin';
    robot.keyTap('s', isMac ? 'command' : 'control');
    // 1000ms delay
    await new Promise(resolve => setTimeout(resolve, 1000));
}

(async () => {
    const baseUrl = 'https://sozialversicherungen.admin.ch/';
    const languages = ['it', 'fr', 'de'];
    const pageNumbers = ['5621', '5622', '5623', '5625', '5624', '5665', '5666', '5667', '5661', '5664',  '5662', '5663', '5659', '5660', '15871', '12918','20314', '5637'];
    const downloadedUrls = new Set();

    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();

    for (const lang of languages) {
        const languageFolder = path.resolve(__dirname, 'downloads', lang);
        if (!fs.existsSync(languageFolder)) {
            fs.mkdirSync(languageFolder, { recursive: true });
        }

        // Intercept requests to handle downloads
        await page._client().send('Page.setDownloadBehavior', {
            behavior: 'allow',
            downloadPath: languageFolder,
        });

        for (const pageNumber of pageNumbers) {
            const url = `${baseUrl}${lang}/f/${pageNumber}`;
            console.log(`Visiting: ${url}`);
            await page.goto(url, { waitUntil: 'networkidle0', timeout: 60000 });


            // Find all download links and filter out versions
            const downloadLinks = await page.evaluate(() => {
                return Array.from(document.querySelectorAll('a.btn.btn-default'))
                    .filter(link => (link.textContent.includes('Download') || link.textContent.includes('Téléchargement')) && !link.href.includes('?version='))
                    .map(link => link.href);
            });

            for (const link of downloadLinks) {
                if (!downloadedUrls.has(link)) {
                    downloadedUrls.add(link);
                    console.log(`Opening PDF: ${link}`);
                    const newPage = await browser.newPage();

                    // Listen for download events
                    const client = await newPage.target().createCDPSession();
                    await client.send('Page.setDownloadBehavior', {
                        behavior: 'allow',
                        downloadPath: languageFolder,
                    });

                    try {
                        // Go to the link and check if it triggers a download
                        const response = await newPage.goto(link, { waitUntil: 'networkidle0', timeout: 60000 });

                        // Check if the response is a PDF
                        const contentType = response.headers()['content-type'];
                        if (contentType && contentType.includes('application/pdf')) {
                            // If it's a PDF, simulate pressing Ctrl+S
                            await newPage.bringToFront();
                            try {
                                await savePageAs();
                            } catch (error) {
                                console.error(`Error triggering download with robotjs: ${error}`);
                            }
                        }
                    } catch (error) {
                        if (error.message.includes('net::ERR_ABORTED')) {
                            console.warn(`Download triggered directly for ${link}, continuing...`);
                        } else {
                            console.error(`Error navigating to ${link}: ${error}`);
                        }
                    }

                    await newPage.close();
                }
            }
        }
    }

    await browser.close();
})();
