# Copyright 2018-2021 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from typing import cast, Optional

import streamlit
from streamlit.errors import StreamlitAPIException
from streamlit.proto.ColorPicker_pb2 import ColorPicker as ColorPickerProto
from streamlit.state.widgets import (
    register_widget,
    WidgetArgs,
    WidgetCallback,
    WidgetDeserializer,
    WidgetKwargs,
)
from .form import current_form_id


class ColorPickerMixin:
    def color_picker(
        self,
        label: str,
        value: Optional[str] = None,
        key: Optional[str] = None,
        help: Optional[str] = None,
        on_change: Optional[WidgetCallback] = None,
        args: Optional[WidgetArgs] = None,
        kwargs: Optional[WidgetKwargs] = None,
    ) -> str:
        """Display a color picker widget.

        Parameters
        ----------
        label : str
            A short label explaining to the user what this input is for.
        value : Optional[str]
            The hex value of this widget when it first renders. If None,
            defaults to black.
        key : Optional[str]
            An optional string to use as the unique key for the widget.
            If this is omitted, a key will be generated for the widget
            based on its content. Multiple widgets of the same type may
            not share the same key.
        help : Optional[str]
            An optional tooltip that gets displayed next to the color picker.
        on_change : Optional[Callable]
            An optional callback invoked when the color_picker value changes.
        args : Optional[Tuple]
            An optional tuple of args to pass to the callback.
        kwargs : Optional[Dict]
            An optional dict of kwargs to pass to the callback.

        Returns
        -------
        str
            The selected color as a hex string.

        Example
        -------
        >>> color = st.color_picker('Pick A Color', '#00f900')
        >>> st.write('The current color is', color)

        """
        # set value default
        if value is None:
            value = "#000000"

        # make sure the value is a string
        if not isinstance(value, str):
            raise StreamlitAPIException(
                """
                Color Picker Value has invalid type: %s. Expects a hex string
                like '#00FFAA' or '#000'.
                """
                % type(value).__name__
            )

        # validate the value and expects a hex string
        match = re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", value)

        if not match:
            raise StreamlitAPIException(
                """
                '%s' is not a valid hex code for colors. Valid ones are like
                '#00FFAA' or '#000'.
                """
                % value
            )

        color_picker_proto = ColorPickerProto()
        color_picker_proto.label = label
        color_picker_proto.default = str(value)
        color_picker_proto.form_id = current_form_id(self.dg)
        if help is not None:
            color_picker_proto.help = help

        deserialize_color_picker: WidgetDeserializer = lambda ui_value: str(
            ui_value if ui_value is not None else value
        )
        current_value, set_frontend_value = register_widget(
            "color_picker",
            color_picker_proto,
            user_key=key,
            on_change_handler=on_change,
            args=args,
            kwargs=kwargs,
            deserializer=deserialize_color_picker,
        )

        if set_frontend_value:
            color_picker_proto.default = current_value
            color_picker_proto.value = current_value
            color_picker_proto.set_value = True

        self.dg._enqueue("color_picker", color_picker_proto)
        return current_value

    @property
    def dg(self) -> "streamlit.delta_generator.DeltaGenerator":
        """Get our DeltaGenerator."""
        return cast("streamlit.delta_generator.DeltaGenerator", self)
