export interface ChangelogEntry {
    version: string;
    date: string;
    title: string;
    description: string;
    changes: string[];
    type: 'major' | 'minor' | 'patch';
}

export const CHANGELOG_DATA: ChangelogEntry[] = [
    {
        version: "1.2.0",
        date: "2026-02-11",
        title: "Delete Signal & UI Improvements",
        description: "Major update introducing signal management and visual enhancements.",
        type: "minor",
        changes: [
            "Added ability to delete signals from the dashboard.",
            "Restored Premium UI design for Signal Cards.",
            "Improved performance of metrics recalculation.",
            "Fixed linting issues in backend services."
        ]
    },
    {
        version: "1.1.5",
        date: "2026-02-10",
        title: "Dashboard Filters",
        description: "Enhanced filtering capabilities for the dashboard.",
        type: "patch",
        changes: [
            "Added Source Filter (All / Manual / Strategy).",
            "Real-time stats updates based on active filters.",
            "Optimized signal feed rendering."
        ]
    },
    {
        version: "1.1.5",
        date: "2026-02-10",
        title: "Dashboard Filters",
        description: "Enhanced filtering capabilities for the dashboard.",
        type: "minor",
        changes: [
            "Added Source Filter (All / Manual / Strategy).",
            "Real-time stats updates based on active filters.",
            "Optimized signal feed rendering."
        ]
    }
];
