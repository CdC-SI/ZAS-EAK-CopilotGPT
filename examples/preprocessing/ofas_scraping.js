const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

(async () => {
    const baseUrl = 'https://sozialversicherungen.admin.ch/';
    const languages = ['it', 'fr', 'de'];
    const pageByTag = [
        {tag:'ahv_services', pages: ['5621', '5622', '5623', '5625', '5624', '5665', '5666', '5667']},
        {tag:'iv_services', pages:['5661', '5664',  '5662', '5663', '5659', '5660', '15871', '12918','20314', '5637']},
        {tag:'el_services', pages:['5638', '5639', '5640']}
    ];
    const banned_urls = ['5543', '5544', '5545'];
    const result = [];

    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    for (const lang of languages) {
        for (const tag of pageByTag) {
            for (const pageNumber of tag.pages) {
                const url = `${baseUrl}${lang}/f/${pageNumber}`;
                console.log(`Visiting: ${url}`);
                await page.goto(url, { waitUntil: 'networkidle0', timeout: 60000 });

                // Find all download links and filter out versions
                const downloadLinks = await page.evaluate(() => {
                    return Array.from(document.querySelectorAll('a.btn.btn-default'))
                        .filter(link => (link.textContent.includes('Download') || link.textContent.includes('Téléchargement')) && !link.href.includes('?version='))
                        .map(link => link.href);
                });

                // Extract subtopics from the breadcrumb list items that do not have banned URLs
                const subtopics = await page.evaluate((banned_urls) => {
                    return Array.from(document.querySelectorAll('ol.breadcrumb li a'))
                        .filter(link => !banned_urls.some(banned => link.href.includes(banned)))
                        .map(item => item.textContent.trim().replace(/\s+/g, '_')) // Only get text if there's no link
                        .join(', '); // Join subtopics with commas
                }, banned_urls);

                // Add each URL with its corresponding tag and subtopics to the result array
                for (const link of downloadLinks) {
                    if (!result.some(item => item.url === link)) { // Check if the URL is already added
                        result.push({ url: link, tag: tag.tag, subtopics: subtopics }); // Associate the tag and subtopics with the URL
                    }
                }
            }
        }
    }

    await browser.close();

    // Output the result array to the JSON file
    fs.writeFileSync(path.resolve(__dirname, 'sources/pdf_urls.json'), JSON.stringify(result, null, 2));
})();
