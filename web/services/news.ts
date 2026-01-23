
import { apiFetch } from "@/lib/api-client";

export interface NewsItem {
    id: number;
    title: string;
    url: string;
    published_at: string;
    source: { title: string };
    currencies: Array<{ code: string; slug: string }>;
}

export const newsService = {
    getNews: async (limit: number = 20) => {
        return apiFetch<{ results: NewsItem[] }>("/news/", {
            params: { limit }
        });
    }
};
