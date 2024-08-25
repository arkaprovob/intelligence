## apache ssi (server side includes)

ssi (server side includes) are directives placed in html pages and evaluated on the server while the pages are being
served. they let you add dynamically generated content to an existing html page without serving the entire page via a
cgi program or other dynamic technology.
for more details, refer to
the [apache ssi documentation](https://httpd.apache.org/docs/current/mod/mod_include.html#includevirtual).

## spaship sync

spaship sync is a process where a scheduler pulls html pages from a remote location into a specific directory of an
environment periodically.

### how it works

1. **configuration injection:** a configuration is injected into the sync engine’s environment, specifying the input
   html file and output directories.
2. **periodic sync:** the sync engine periodically pulls from the source location and downloads it into the destination
   directories.

### sync and ssi

spaship sync uses the ssi technique to sync common sections like headers and footers across pages. it utilizes
`<!--#include virtual…` to reuse these common sections on every page.
if a file mentioned in `<!--#include virtual…` does not exist in the destination folder, the apache server will throw
errors, and no content on the page will be accessible.

### sync high-level illustration

![sync illustration](./images/sync_1.png)

### anatomy of sync config structure

![sync config structure](./images/sync_2.png)

- `name`: name of the page.
- `interval`: frequency of polling remote contents into the destination (in seconds).
- `source.url`: remote location of the source.
- `source.sub_paths`: array containing sub-paths (optional).
- `dest.path`: parent folder location for downloading the page(s).
- `dest.filename`: destination file name in the directory.

### sample ssi application

download a [sample html ssi page](#) with `<!--#include virtual` tags for header and footer. adjust the sync config to
pull html sources into specific directories mentioned in the `virtual` attribute.
**sample html**
![sample html](./images/sync_3.png)

### implementational details

1. **update sync option in manager:**
   ![update sync](./images/sync_4.png)
2. **select environment and provide config:**
   ![environment config](./images/sync_5.png)