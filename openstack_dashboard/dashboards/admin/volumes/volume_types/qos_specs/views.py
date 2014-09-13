# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon.utils.memoized import memoized  # noqa

from openstack_dashboard import api
from openstack_dashboard.dashboards.admin.volumes.volume_types.qos_specs \
    import forms as project_forms
from openstack_dashboard.dashboards.admin.volumes.volume_types.qos_specs \
    import tables as project_tables


class QosSpecMixin(object):
    @memoized
    def get_context_data(self, **kwargs):
        context = super(QosSpecMixin, self).get_context_data(**kwargs)
        # Note the use of self.kwargs instead of the parameter kwargs.
        # This is needed for consistency when dealing with both
        # index views and forms (i,e, EditView). With forms,
        # the parameter kwargs contains form layout information,
        # not key data that is needed here.
        if 'key' in self.kwargs:
            context['key'] = self.kwargs['key']
            qos_spec_id = context['key']
        if 'qos_spec_id' in self.kwargs:
            context['qos_spec_id'] = self.kwargs['qos_spec_id']
            qos_spec_id = context['qos_spec_id']

        try:
            qos_list = api.cinder.qos_spec_get(self.request, qos_spec_id)
            context['qos_spec_name'] = qos_list.name
        except Exception:
            context['qos_spec_name'] = _('undefined')

        return context


class IndexView(QosSpecMixin, forms.ModalFormMixin, tables.DataTableView):
    table_class = project_tables.SpecsTable
    template_name = 'admin/volumes/volume_types/qos_specs/index.html'

    def get_data(self):
        try:
            qos_spec_id = self.kwargs['qos_spec_id']
            qos_list = api.cinder.qos_spec_get_keys(self.request, qos_spec_id)
        except Exception:
            qos_list = []
            exceptions.handle(self.request,
                              _('Unable to retrieve QOS spec list.'))
        return qos_list


class EditView(QosSpecMixin, forms.ModalFormView):
    form_class = project_forms.EditQosSpec
    template_name = 'admin/volumes/volume_types/qos_specs/edit.html'
    success_url = 'horizon:admin:volumes:volume_types:qos_specs:index'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['qos_spec_id'],))

    def get_initial(self):
        qos_spec_id = self.kwargs['qos_spec_id']
        key = self.kwargs['key']
        try:
            qos_specs = api.cinder.qos_spec_get(self.request, qos_spec_id)
        except Exception:
            qos_specs = {}
            exceptions.handle(self.request,
                              _('Unable to retrieve QOS spec '
                                'details.'))
        return {'qos_spec_id': qos_spec_id,
                'key': key,
                'value': qos_specs.specs.get(key, '')}
