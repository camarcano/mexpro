/**
 * Shared AG Grid configuration and value formatters for MexPro.
 * Following the tbox pattern: dynamic columns from API, custom formatters.
 */

const MexProGrid = {
    /** Standard value formatters keyed by name (referenced in column defs) */
    formatters: {
        fixed0: (params) => {
            if (params.value == null) return '\u2014';
            return Math.round(params.value).toString();
        },
        fixed1: (params) => {
            if (params.value == null) return '\u2014';
            return Number(params.value).toFixed(1);
        },
        fixed2: (params) => {
            if (params.value == null) return '\u2014';
            return Number(params.value).toFixed(2);
        },
        fixed3: (params) => {
            if (params.value == null) return '\u2014';
            return Number(params.value).toFixed(3);
        },
        pct1: (params) => {
            if (params.value == null) return '\u2014';
            return Number(params.value).toFixed(1) + '%';
        },
    },

    /** Apply formatter strings from server column defs to actual functions */
    applyFormatters(colDefs) {
        return colDefs.map(col => {
            if (typeof col.valueFormatter === 'string' && this.formatters[col.valueFormatter]) {
                col.valueFormatter = this.formatters[col.valueFormatter];
            }
            col.sortable = col.sortable !== false;
            col.filter = col.filter !== false;
            col.resizable = col.resizable !== false;
            return col;
        });
    },

    /** Default grid options */
    defaultOptions: {
        pagination: true,
        paginationPageSize: 25,
        paginationPageSizeSelector: [10, 25, 50, 100],
        animateRows: true,
        domLayout: 'normal',
        autoSizeStrategy: {
            type: 'fitCellContents',
        },
        defaultColDef: {
            sortable: true,
            filter: true,
            resizable: true,
            minWidth: 50,
        },
    },

    /**
     * Initialize an AG Grid from an API endpoint.
     * @param {string} containerId - DOM element ID
     * @param {string} apiUrl - URL returning {columns, rows}
     * @param {object} extraOptions - Additional grid options
     * @returns {Promise<object>} The grid API
     */
    async init(containerId, apiUrl, extraOptions = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container #${containerId} not found`);
            return null;
        }

        try {
            const response = await fetch(apiUrl);
            const data = await response.json();

            const columnDefs = this.applyFormatters(data.columns || []);
            const rowData = data.rows || [];

            const gridOptions = {
                ...this.defaultOptions,
                ...extraOptions,
                columnDefs,
                rowData,
            };

            const gridApi = agGrid.createGrid(container, gridOptions);
            return gridApi;
        } catch (err) {
            console.error('Failed to initialize grid:', err);
            container.innerHTML = '<div class="alert alert-danger">Failed to load data.</div>';
            return null;
        }
    },
};
