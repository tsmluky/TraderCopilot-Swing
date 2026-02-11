import { apiFetch } from "@/lib/api-client"

export interface ChangelogEntry {
    id?: number;
    version: string;
    date: string;
    title: string;
    description: string;
    changes: string[]; // JSON array
    type: 'major' | 'minor' | 'patch';
    created_at?: string;
}

export interface ChangelogCreate {
    version: string;
    date: string;
    title: string;
    description: string;
    changes: string[];
    type: string;
}

export const changelogService = {
    getChangelog: async (): Promise<ChangelogEntry[]> => {
        return apiFetch("/changelog/");
    },

    createEntry: async (entry: ChangelogCreate): Promise<ChangelogEntry> => {
        return apiFetch("/changelog/", {
            method: "POST",
            body: JSON.stringify(entry),
        });
    },

    deleteEntry: async (version: string): Promise<void> => {
        return apiFetch(`/changelog/${version}`, {
            method: "DELETE",
        });
    }
};
