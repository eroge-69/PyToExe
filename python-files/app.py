import pyvisual as pv
from ui.ui import create_ui
import time
import threading

# ===================================================
# ================ 1. CORE APP LOGIC ================
# ===================================================

class TodoApp:
    def __init__(self):
        self.checkbox_count = 0
        self.CHECKBOX_SPACING = 50
        self.created_checkboxes = []
        self.ui = None
        
    def initialize(self, ui):
        """Initialize the app with UI references"""
        self.ui = ui
        self._hide_template_elements()
        self._attach_events()
    
    def _hide_template_elements(self):
        """Hide template elements that shouldn't be visible initially"""
        elements_to_hide = [
            'checkbox_item',
            'delete_text',
            'limit_alert'
        ]
        for element_name in elements_to_hide:
            if element_name in self.ui["page_0"]:
                self.ui["page_0"][element_name].is_visible = False
    
    def _attach_events(self):
        """Attach event handlers to UI components"""
        self.ui["page_0"]["add_button"].on_click = self._on_add_click
    
    def _on_add_click(self, button):
        """Handle add button click"""
        text = self.ui["page_0"]["text_input"].text
        self.ui["page_0"]["text_input"].text = ""  # Clear input immediately
        if text.strip():
            self.add_todo_item(text)
    
    def _get_base_checkbox_y(self):
        """Get the y position from the template checkbox"""
        return self.ui["page_0"]["checkbox_item"].y
    
    def _calculate_max_tasks(self):
        """Calculate maximum tasks that can fit in the window"""
        window_height = self.ui["window"].height() if callable(self.ui["window"].height) else self.ui["window"].height
        start_y = self._get_base_checkbox_y()
        available_height = window_height - start_y - 50  # 50px buffer at bottom
        return available_height // self.CHECKBOX_SPACING
    
    def _hide_alert_after_delay(self):
        """Hide the alert after a delay using a separate thread"""
        time.sleep(4)
        try:
            self.ui["page_0"]["limit_alert"].is_visible = False
        except:
            pass  # Ignore any errors if elements are not found
    
    def _on_checkbox_toggle(self, checkbox, event=None):
        """Handle checkbox toggle event
        
        The event system passes both the checkbox and the event,
        so we need to accept both parameters even if we don't use the event.
        """
        checkbox.strikeout = checkbox.is_checked
        if checkbox.is_checked:
            checkbox.font_color = (254, 100, 61, 1)
        else:
            template_checkbox = self.ui["page_0"]["checkbox_item"]
            checkbox.font_color = template_checkbox.font_color
    
    def _on_delete_click(self, delete_button, event=None):
        """Handle delete button click event"""
        # Find the index of the task being deleted
        delete_index = next((i for i, (cb, btn) in enumerate(self.created_checkboxes) 
                           if btn == delete_button), -1)
        
        if delete_index != -1:
            # Get the checkbox associated with this delete button
            checkbox, _ = self.created_checkboxes[delete_index]
            
            # Hide the widgets being deleted
            checkbox.is_visible = False
            delete_button.is_visible = False
            
            # Remove from our tracking list
            self.created_checkboxes.pop(delete_index)
            
            # Update checkbox count
            self.checkbox_count -= 1
            
            # Hide the limit alert if it's visible
            try:
                self.ui["page_0"]["limit_alert"].is_visible = False
            except:
                pass
            
            # Reposition all remaining tasks
            delete_y_offset = self.ui["page_0"]["delete_text"].y - self.ui["page_0"]["checkbox_item"].y
            for i, (cb, btn) in enumerate(self.created_checkboxes):
                new_y = self._get_base_checkbox_y() + (i * self.CHECKBOX_SPACING)
                cb.y = new_y
                btn.y = new_y + delete_y_offset  # Use the same offset for alignment
    
    def add_todo_item(self, text):
        """Add a new todo item to the list"""
        if not text.strip():
            return
            
        # Check if adding new task would exceed the limit
        if self.checkbox_count >= self._calculate_max_tasks():
            # Show limit alert
            self.ui["page_0"]["limit_alert"].is_visible = True
            
            # Start a thread to hide the alert after delay
            threading.Thread(target=self._hide_alert_after_delay, daemon=True).start()
            return

        # Copy UI elements from templates
        new_elements = self._copy_ui_elements([
            self.ui["page_0"]["checkbox_item"],
            self.ui["page_0"]["delete_text"]
        ])
        
        # Calculate positions
        y_position = self._get_base_checkbox_y() + (self.checkbox_count * self.CHECKBOX_SPACING)
        delete_y_offset = self.ui["page_0"]["delete_text"].y - self.ui["page_0"]["checkbox_item"].y
        
        # Get references to the copied elements
        new_checkbox = list(new_elements.values())[0]
        delete_button = list(new_elements.values())[1]
        
        # Configure elements
        new_checkbox.y = y_position
        new_checkbox.is_visible = True
        new_checkbox.text = text
        
        delete_button.y = y_position + delete_y_offset
        delete_button.is_visible = True
        delete_button.text = "x"

        # Bind events
        new_checkbox.on_click = lambda cb=new_checkbox, event=None: self._on_checkbox_toggle(cb, event)
        delete_button.on_click = lambda btn=delete_button, event=None: self._on_delete_click(btn, event)

        # Store references
        self.created_checkboxes.append((new_checkbox, delete_button))
        self.checkbox_count += 1
    
    def _copy_ui_elements(self, elements_to_copy):
        """
        Create copies of UI elements and return a dictionary of the copied elements
        """
        copied_elements = {}
        window = self.ui["window"]
        
        for i, element in enumerate(elements_to_copy):
            # Reset template checkbox state before copying
            if hasattr(element, 'is_checked'):
                element.is_checked = False
                element.strikeout = False
            
            # Get the element's class and prepare attributes
            element_class = type(element)
            
            # Get width and height values
            width = element.width() if callable(element.width) else element.width
            height = element.height() if callable(element.height) else element.height
            
            # Get non-callable attributes for copying
            attrs = {attr: getattr(element, attr) for attr in dir(element) 
                    if not attr.startswith('_') and not callable(getattr(element, attr))}
            
            # Prepare default attributes
            default_attrs = {
                'container': window,
                'x': attrs.get('x', 0),
                'y': attrs.get('y', 0),
                'width': width,
                'height': height,
                'text': attrs.get('text', ''),
                'is_visible': False  # Initially hidden
            }
            
            # Add all other attributes from the original element
            for attr, value in attrs.items():
                if attr not in default_attrs:
                    default_attrs[attr] = value
            
            # Create new element with all attributes
            new_element = element_class(**default_attrs)
            
            # Store the copied element with its original name
            element_name = element.tag if hasattr(element, 'tag') and element.tag else f"copied_{i}"
            copied_elements[element_name] = new_element
        
        return copied_elements

# ===================================================
# ============== 2. MAIN FUNCTION ==================
# ===================================================

def main():
    app = pv.PvApp()
    ui = create_ui()
    
    # Initialize todo app
    todo_app = TodoApp()
    todo_app.initialize(ui)
    
    # Show window and run app
    ui["window"].show()
    app.run()

if __name__ == '__main__':
    main()