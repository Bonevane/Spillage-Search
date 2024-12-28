export function validateMediumUrl(url: string): boolean {
    try {
        const parsedUrl = new URL(url);
        return (
            parsedUrl.hostname === 'medium.com' ||
            parsedUrl.hostname.endsWith('.medium.com')
        );
        } catch {
        return false;
    }
}