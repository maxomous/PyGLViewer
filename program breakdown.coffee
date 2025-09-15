
Changes Needed:
    on object creation, add strait to static / dynamic buffer
    on object set_data
        give a batch id
        AND ADD glBufferData (to resize) glBufferSubData (to update)
        remove batch_renderer_update but handle obj.remove() from static_buffer / dyn...
    # shouldnt be updating every frame
    # static shouldnt be cleared also
    render_object is not object with shapes stored directly instead

############################
IN PYGLVIEWER (CURRENT)
############################

each frame: renderer.draw(view_matrix, projection_matrix ...) -> 
        
    # batch_renderer_update (PROPOSED) remove this
    #     batch_renderer.clear() 
    #         self.static_buffer.clear() *BOTH*
    #         self.dynamic_buffer.clear() (clears batched)
        
    #     for render_obj for obj in self.objects:
    #         batch_renderer.add_object_to_batch(render_object)
    #             static_or_dynamic_buffer.add_object_to_buffer(render_object) # Create key and render_object to static_buffer.batches or dynamic


    batch_renderer.render 
        
        # batch_renderer.update_buffers() -> (PROPOSED) remove this
    
        #     static_buffer.update_buffers() ->           # batch_renderer.static_buffer
        #         verticies, indices = [obj.vertex_data, obj.index_data for obj in batch_data in self.batches]
        #         vertex_buffer.update_data(verticies)  # batch_renderer.static_buffer.vertex_buffer
        #         index_buffer.update_data(indices)  
        #             glBufferData    # to resize     # also called in vb/ib constructor 
        #             glBufferSubData     # to update
            
        #     dynamic_buffer.update_buffers() -> 
        #         ... # ALSO!
        
        render_buffer(static_buffer)
        render_buffer(dynamic_buffer)
            
            bind(vao & vb & ib)
                for objects in batches:
                    set shader (if not current)
                    for each object in objects:
                        shader.set_model_matrix()
                        glDrawElements()
            unbind(vao & vb & ib & shader)




object = renderer.add_object(Object(static=true))
    renderer.objects.append(object)

object.set_shapes()
     for each shape create a RenderObject(static=true)
     for each shape render_object.set_shape()
        vertex_data, index_data = shape.get_vertices(), shape.get_indices()
    ### BUT NOT ACTUALLY DONE ANYTHING WITH IT ###


############################
IN APPLICATION (CURRENT)
############################


# create & set static
self.grid = self.renderer.add_object(Object(static=True)
    .set_shapes(Shapes.grid()).set_transform_matrix(Transform(translate=...)))

# create dynamic
self.renderables['original_elements'] = Renderable(objects=create_objects(...), images=None, texts=None)    
    
    
        
update_scene():
    if update.has_flag(UpdateFlag.OBJECTS):
        clear_renderable_objects()
            for name in renderables.items():
                renderer.remove_objects(self.renderables[name]['objects'])
                renderables[name]['objects'] = []
                _remove_blank_renderables()
                
        create_render_objects()
            for obj in self.renderables['original_elements']:
                object.set_shapes(Shapes.beam(p0=e['p0'], p1=e['p1'], width=e['height'], height=e['width'], colour=colour))
                

############################
WHAT WOULD BE NICER
no need to call create_render_objects()
############################


# vertex_data & index_data is now updated when a shape's vertices change so we can 
DONE: Store the [shape] directly in object



# use object name to read a map
object_map = {}
object_map['my object'] = { 'is_static': true, 'batch_key': 'STATIC_LW_...'}

def get_object():
    buffer = static_buffer if object_map['my object']['is_static'] else dynamic_buffer
    object = buffer[object_map['my object']['batch_key']]
    return object
    

renderer.update_object('my_object', shape, transform, is_static=true)
    if not exist or len(shapes) has changed: 
        object = Object()
        self.renderer.add_object_to_batch_buffer(f'my_object_{i}')
            buffer = self.static_buffer if render_object._static else self.dynamic_buffer # # add object to static / dynamic batch buffer
            buffer.add_object_to_buffer(render_object)
    object._set_shapes(Shapes.beam(p0=e['p0'], p1=e['p1'], width=e['height'], height=e['width'], colour=colour))
    object._set_point_size():
    object._set_line_width():
    object._set_point_shape():
    object._set_alpha():
    object._set_static(): # todo remove static from Object / RenderObject entirely?? 
        object_map['my_object']['buffer']
    object._set_selectable():
    object._set_metadata() # todo add this
    object._set_transform_matrix()
    object._toggle_select()
    renderer.set_object_transform('my_object', transform)
    renderer.set_object_translate('my_object', translate)
    update_batch_key()
        batch_key = create_batch_key()
        if changed: move to new location, delete old, 
        set object_map['my_object']['batch_key']




renderer.delete_object('my_object')

renderer.get_object_transform('my_object')
renderer.get_object_translate('my_object')

renderer.get_object_bounds('my_object')
renderer.get_object_mid_point('my_object')

renderer.select_object('my_object')
renderer.deselect_object('my_object')
renderer.toggle_object('my_object')









    still todo
        - think about text and images
        - BatchRenderer(buffers={
                'static':  RenderBuffer(10000, 10000, GL_STATIC_DRAW),
                'dynamic':  RenderBuffer(10000, 10000, GL_DYNAMIC_DRAW),
            }) # to allow n buffer (might be hard see add_object_to_batch)
            # rename BatchRenderer to Buffers
            # BatchRenderer._render_buffer() should be in Buffer?


TO TEST:
    Object.get_bounds()
rename draw_type to primitive
check vertex_offset & index_offset arent incrementing constantly