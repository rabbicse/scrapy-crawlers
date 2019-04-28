from scrapy.exporters import CsvItemExporter

from scrapy.conf import settings


class CosylabCsvExporter(CsvItemExporter):
    def __init__(self, *args, **kwargs):
        fields_to_export = settings.get('EXPORT_FIELDS', [])
        if fields_to_export:
            kwargs['fields_to_export'] = fields_to_export

        super(CosylabCsvExporter, self).__init__(*args, **kwargs)
