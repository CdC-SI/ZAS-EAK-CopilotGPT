const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

(async () => {
    const baseUrl = 'https://sozialversicherungen.admin.ch/';
    const languages = ['it', 'fr', 'de'];
    const pageNumbers = ['5621', '5622', '5623', '5625', '5624', '5665', '5666', '5667', '5661', '5664',  '5662', '5663', '5659', '5660', '15871', '12918','20314', '5637', '5638', '5639', '5640'];
    const pdfUrls = [];

    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    for (const lang of languages) {
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

            // Add unique links to the pdfUrls array
            for (const link of downloadLinks) {
                if (!pdfUrls.includes(link)) {
                    pdfUrls.push(link);
                }
            }
        }
    }

    await browser.close();

    // Output the list of PDF URLs
    console.log('PDF URLs:', pdfUrls);

    // Optionally, save the URLs to a file
    fs.writeFileSync(path.resolve(__dirname, 'sources/pdf_urls.json'), JSON.stringify(pdfUrls, null, 2));
})();
