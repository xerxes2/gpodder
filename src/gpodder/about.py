# -*- coding: utf-8 -*-
#
# gPodder - A media aggregator and podcast client
# Copyright (c) 2005-2011 Thomas Perl and the gPodder Team
#
# gPodder is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# gPodder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gpodder
from gpodder.qtui import qtutil
_ = gpodder.gettext

about_name = 'gPodder'
about_icon_name = 'gpodder'
about_text = _('A podcast client with focus on usability')
about_website = 'http://gpodder.org'
about_bugtracker = 'http://bugs.gpodder.org'
about_donate = 'http://gpodder.org/donate'
about_copyright = _('Copyright (c) 2005-2011 The gPodder Project')
about_authors = ['Thomas Perl']
about_contributors = []

_file = open(qtutil.find_data_file("credits.txt"))
_list = _file.read().encode("utf-8").splitlines()
_file.close()
for i in _list:
    about_contributors.append(i)
