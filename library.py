from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsVectorLayer,
    QgsField,
    QgsSpatialIndex,
    QgsFeatureRequest,
    QgsExpression,
    QgsPointXY,
    QgsWkbTypes
)

def interpolate_line_segment(line_segment, interpolate_interval):
    list_interpolate_point_feature = []
    interpolate_dist = 0
    while interpolate_dist < line_segment.length():
        interpolate_point = line_segment.interpolate(interpolate_dist)
        feat = QgsFeature()
        feat.setGeometry(interpolate_point)
        list_interpolate_point_feature.append(feat)
        interpolate_dist += interpolate_interval
    return list_interpolate_point_feature

def interpolate_line(list_of_line_feature, interpolate_interval):
    list_interpolate_point_feature = []
    for line_feat in list_of_line_feature:
        line_geom = line_feat.geometry()
        if line_geom.isMultipart():
            line_coord = line_geom.asMultiPolyline()
            for line in line_coord:
                for index in range(len(line) - 1):
                    first_point = line[index]
                    second_point = line[index + 1]
                    segment_geom = QgsGeometry.fromPolylineXY([first_point, second_point])
                    points = interpolate_line_segment(segment_geom, interpolate_interval)
                    list_interpolate_point_feature += points
                last_point = QgsGeometry.fromPointXY(line[-1])
                last_point_feat = QgsFeature()
                last_point_feat.setGeometry(last_point)
                list_interpolate_point_feature.append(last_point_feat)
        else:
            line_coord = line_geom.asPolyline()
            for index in range(len(line_coord) - 1):
                first_point = line_coord[index]
                second_point = line_coord[index + 1]
                segment_geom = QgsGeometry.fromPolylineXY([first_point, second_point])
                points = interpolate_line_segment(segment_geom, interpolate_interval)
                list_interpolate_point_feature += points
            last_point = QgsGeometry.fromPointXY(line_coord[-1])
            last_point_feat = QgsFeature()
            last_point_feat.setGeometry(last_point)
            list_interpolate_point_feature.append(last_point_feat)

    return list_interpolate_point_feature

def apply_effect(median_layer, effect_type, ratio=None):
    if effect_type == "full":
        return median_layer

    elif effect_type == "half":
        if ratio is None or len(ratio) != 2 or any(r <= 0 for r in ratio):
            raise ValueError("Ratio must be a tuple (state_a_ratio, state_b_ratio) and both must be greater than 0.")
        
        state_a_ratio, state_b_ratio = ratio
        total_ratio = state_a_ratio + state_b_ratio
        
        adjusted_median_layer = QgsVectorLayer("LineString?crs=" + median_layer.crs().authid(), "Adjusted Median Line", "memory")
        adjusted_layer_pr = adjusted_median_layer.dataProvider()
        
        for feat in median_layer.getFeatures():
            geometry = feat.geometry()
            adjusted_points = []
            for i in range(0, int(geometry.length()), 1):
                point_on_line = geometry.interpolate(i)
                adjusted_points.append(point_on_line)

            adjusted_geometry_a = QgsGeometry.fromPolylineXY(adjusted_points[:int(len(adjusted_points) * (state_a_ratio / total_ratio))])
            adjusted_geometry_b = QgsGeometry.fromPolylineXY(adjusted_points[int(len(adjusted_points) * (state_a_ratio / total_ratio)):])

            adjusted_geometry = adjusted_geometry_a.combine(adjusted_geometry_b)

            adjusted_feat = QgsFeature()
            adjusted_feat.setGeometry(adjusted_geometry)
            adjusted_layer_pr.addFeature(adjusted_feat)
        
        adjusted_median_layer.updateExtents()
        return adjusted_median_layer

    elif effect_type == "null":
        null_effect_layer = QgsVectorLayer("LineString?crs=" + median_layer.crs().authid(), "Null Effect Layer", "memory")
        null_layer_pr = null_effect_layer.dataProvider()
        
        for feat in median_layer.selectedFeatures():
            null_layer_pr.addFeature(feat)

        null_effect_layer.updateExtents()
        return null_effect_layer

    else:
        raise ValueError("Invalid effect type. Choose 'full', 'half', or 'null'.")




def line_to_point_layer_new(
    list_feat,
    crs,
    layer_name="layer_ttk",  # Use layer_ttk parameter instead of the fixed "Point Layer"
    id_name="point_id",
    id_prefix="",
    filepath="memory",
    interpolate_interval=0,
):
    """Convert list of line feature into a point layer.

    Args:
        list_feat (list): List of line feature
        crs (epsg crs): crs information
        layer_ttk (QgsVectorLayer): Point layer to store results
        id_name (str, optional): [description]. Defaults to "point_id".
        id_prefix (str, optional): [description]. Defaults to "".
        filepath (str, optional): [description]. Defaults to "memory".
        interpolate_interval (int, optional): [description]. Defaults to 0.

    Returns:
        QgsVectorLayer: Point Layer
    """
    layer_ttk = QgsVectorLayer("Point?crs=" + crs, layer_name, filepath)
    point_layer_pr = layer_ttk.dataProvider()
    point_layer_pr.addAttributes([QgsField("point_id", QVariant.String)])
    layer_ttk.updateFields()

    point_id = 0


    list_geom = combine_geometries([feat.geometry() for feat in list_feat.getFeatures()])
    
    for line_geom in list_geom:
        if line_geom.isMultipart():
            multi_line = line_geom.asMultiPolyline()
            for line_coord in multi_line:
                for index in range(len(line_coord) - 1):
                    first_point = line_coord[index]
                    if interpolate_interval > 0:
                        next_point = line_coord[index + 1]
                        segment_geom = QgsGeometry.fromPolylineXY(
                            [first_point, next_point]
                        )
                        point_feats = interpolate_line_segment(
                            segment_geom, interpolate_interval
                        )
                        for point_feat in point_feats:
                            point_feat.setAttributes([id_prefix + str(point_id)])
                            point_id += 1
                            point_layer_pr.addFeature(point_feat)
                    else:
                        point_geom = QgsGeometry.fromPointXY(first_point)
                        point_feat = QgsFeature()
                        point_feat.setGeometry(point_geom)
                        point_feat.setAttributes([id_prefix + str(point_id)])
                        point_id += 1
                        point_layer_pr.addFeature(point_feat)
                last_point = QgsGeometry.fromPointXY(line_coord[-1])
                last_point_feat = QgsFeature()
                last_point_feat.setGeometry(last_point)
                last_point_feat.setAttributes([id_prefix + str(point_id)])
                point_layer_pr.addFeature(last_point_feat)
        else:
            line_coord = line_geom.asPolyline()
            for index in range(len(line_coord) - 1):
                first_point = line_coord[index]
                if interpolate_interval > 0:
                    next_point = line_coord[index + 1]
                    segment_geom = QgsGeometry.fromPolylineXY(
                        [first_point, next_point]
                    )
                    point_feats = interpolate_line_segment(
                        segment_geom, interpolate_interval
                    )
                    for point_feat in point_feats:
                        point_feat.setAttributes([id_prefix + str(point_id)])
                        point_id += 1
                        point_layer_pr.addFeature(point_feat)
                else:
                    point_geom = QgsGeometry.fromPointXY(first_point)
                    point_feat = QgsFeature()
                    point_feat.setGeometry(point_geom)
                    point_feat.setAttributes([id_prefix + str(point_id)])
                    point_id += 1
                    point_layer_pr.addFeature(point_feat)
            last_point = QgsGeometry.fromPointXY(line_coord[-1])
            last_point_feat = QgsFeature()
            last_point_feat.setGeometry(last_point)
            last_point_feat.setAttributes([id_prefix + str(point_id)])
            point_layer_pr.addFeature(last_point_feat)

    layer_ttk.startEditing()
    layer_ttk.commitChanges()
    layer_ttk.updateExtents()
    return layer_ttk  # Return the modified layer

def combine_geometries(list_of_geometry):
    g = list_of_geometry[0]
    for geom in list_of_geometry:
        g = g.combine(geom)
    if g.isMultipart():
        list_result_geometry = [QgsGeometry().fromPolylineXY(geom) for geom in g.asMultiPolyline()]
    else:
        list_result_geometry = [g]
    return list_result_geometry

def line_feature_list_to_layer(
    list_feat,
    crs,
    layer_name="Line Layer",
    id_name="line_id",
    filepath="memory"
):
    line_layer = QgsVectorLayer("Linestring?crs=" + crs, layer_name, filepath)
    line_layer_pr = line_layer.dataProvider()

    for feat in list_feat:
        line_layer_pr.addFeature(feat)
    line_layer.startEditing()
    line_layer.commitChanges()
    return line_layer

def merge_line_layers(layer_ttk_a, layer_ttk_b):
    """
    Merges two line layers into one.
    """
    # Get the coordinate reference system (CRS) of the first layer
    crs = layer_ttk_a.crs().authid()
    
    # Create a new memory layer for the merged lines
    layer_ttk = QgsVectorLayer(
        "LineString?crs=" + crs,
        "merged_line_layer",
        "memory"
    )
    
    # Get the data provider for the new layer
    line_layer_pr = layer_ttk.dataProvider()
    
    # Add attributes from the first line layer
    line_layer_pr.addAttributes(layer_ttk_a.fields())
    layer_ttk.updateFields()

    # Extract features from both layers
    list_a = [f for f in layer_ttk_a.getFeatures()]
    list_b = [f for f in layer_ttk_b.getFeatures()]

    # Combine the lists of features
    list_f = list_a + list_b
    
    # Add combined features to the new layer
    line_layer_pr.addFeatures(list_f)
    
    # Start editing and commit changes on the QgsVectorLayer
    layer_ttk.startEditing()
    layer_ttk.commitChanges()  # Commit changes on the QgsVectorLayer
    
    return layer_ttk  # Return the merged line layer

def merge_point_layers(layer_ttk_a, layer_ttk_b):
    """
    Merges two point layers into one.
    """
    crs = layer_ttk_a.crs().authid()
    
    # Create a new memory layer for the merged points
    layer_ttk = QgsVectorLayer(
        "Point?crs=" + crs,
        "merged_point_layer",
        "memory"
    )
    
    point_layer_pr = layer_ttk.dataProvider()
    
    # Add attributes from the first point layer
    point_layer_pr.addAttributes(layer_ttk_a.fields())
    layer_ttk.updateFields()

    # Extract features from both layers
    list_a = [f for f in layer_ttk_a.getFeatures()]
    list_b = [f for f in layer_ttk_b.getFeatures()]
    
    # Combine the lists of features
    list_f = list_a + list_b
    
    # Add combined features to the new layer
    point_layer_pr.addFeatures(list_f)
    
    # Start editing and commit changes on the QgsVectorLayer
    layer_ttk.startEditing()
    layer_ttk.commitChanges()  # Commit changes on the QgsVectorLayer
    
    return layer_ttk  # Return the merged point layer

def create_voronoi(merged_pt_layer):
    spatial_index = QgsSpatialIndex(merged_pt_layer.getFeatures())
    list_feat = [feat for feat in merged_pt_layer.getFeatures()]
    list_point = [feat.geometry().asPoint() for feat in list_feat]

    geom_multipoint = QgsGeometry.fromMultiPointXY(list_point)
    voronoi_diagram = geom_multipoint.voronoiDiagram()
    vd_layer = QgsVectorLayer("MultiPolygon?crs=" + merged_pt_layer.crs().authid(), "Voronoi", "memory")
    vd_layer_pr = vd_layer.dataProvider()
    vd_layer_pr.addAttributes([QgsField("voroID", QVariant.Int), QgsField("point_id", QVariant.String)])
    vd_layer.updateFields()
    vd_id = 0
    for geom in voronoi_diagram.asGeometryCollection():
        voronoi_feat = QgsFeature()
        voronoi_feat.setGeometry(geom)

        intersect_idx = spatial_index.intersects(geom.boundingBox())
        req = QgsFeatureRequest().setFilterFids(intersect_idx)
        req_feat = [feat for feat in merged_pt_layer.getFeatures(req)]
        for feat in req_feat:
            if feat.geometry().intersects(geom):
                pid = feat["point_id"]

        voronoi_feat.setAttributes([vd_id, pid])
        vd_layer_pr.addFeature(voronoi_feat)
        vd_id += 1
    vd_layer.startEditing()
    vd_layer.commitChanges()
    vd_layer.updateExtents()
    return vd_layer

def create_delaunay_triangulation(merged_pt_layer):
    spatial_index = QgsSpatialIndex(merged_pt_layer.getFeatures())
    list_feat = [feat for feat in merged_pt_layer.getFeatures()]
    list_point = [feat.geometry().asPoint() for feat in list_feat]

    geom_multipoint = QgsGeometry.fromMultiPointXY(list_point)
    delaunay_triangulation = geom_multipoint.delaunayTriangulation()

    dt_layer = QgsVectorLayer("MultiPolygon?crs=" + merged_pt_layer.crs().authid(), "Delaunay Triangulation", "memory")
    dt_layer_pr = dt_layer.dataProvider()
    dt_layer_pr.addAttributes([QgsField("delaunayID", QVariant.Int), QgsField("first_point", QVariant.String), QgsField("second_point", QVariant.String), QgsField("third_point", QVariant.String), QgsField("valid_triangle", QVariant.String)])
    dt_layer.updateFields()
    dt_id = 0
    for geom in delaunay_triangulation.asGeometryCollection():
        delaunay_feat = QgsFeature()
        delaunay_feat.setGeometry(geom)

        point_list = []
        intersect_idx = spatial_index.intersects(geom.boundingBox())
        req = QgsFeatureRequest().setFilterFids(intersect_idx)
        req_feat = [feat for feat in merged_pt_layer.getFeatures(req)]
        for feat in req_feat:
            if feat.geometry().touches(geom):
                point_list.append(feat)

        list_attr = []
        for point in point_list:
            list_attr.append(point["point_id"][0])
        unique_attr = list(set(list_attr))
        if len(unique_attr) > 1:
            valid_triangle = "valid"
        else:
            valid_triangle = "invalid"
        delaunay_feat.setAttributes([dt_id, point_list[0]["point_id"], point_list[1]["point_id"], point_list[2]["point_id"], valid_triangle])
        dt_layer_pr.addFeature(delaunay_feat)
        dt_id += 1
    dt_layer.startEditing()
    dt_layer.commitChanges()
    dt_layer.updateExtents()
    return dt_layer

def valid_delaunay_triangulation(dt_layer, list_feature_a, list_feature_b):
    valid_delaunay_req = QgsFeatureRequest(QgsExpression("\"valid_triangle\" = 'valid'"))
    valid_delaunay_list = [feat.geometry() for feat in dt_layer.getFeatures(valid_delaunay_req)]
    valid_delaunay = valid_delaunay_list[0]
    for geom in valid_delaunay_list[1:]:
        valid_delaunay = valid_delaunay.combine(geom)

    valid_dt_layer = QgsVectorLayer("Polygon?crs=" + dt_layer.crs().authid(), "Valid Area", "memory")
    valid_dt_layer_pr = valid_dt_layer.dataProvider()
    geom_a = [feat.geometry() for feat in list_feature_a]
    geom_b = [feat.geometry() for feat in list_feature_b]

    geom_list = []
    for ga in geom_a:
        for gb in geom_b:
            if ga.intersects(gb):
                geom_list.append(ga)
                geom_list.append(gb)
    if len(geom_list) > 0:
        geom_combine = geom_list[0]
        for geom in geom_list[1:]:
            geom_combine = geom_combine.combine(geom)
        result, new_geometries, point_xy = valid_delaunay.splitGeometry(geom_combine.asPolyline(), True)
        for geom in [valid_delaunay] + new_geometries:
            feat = QgsFeature()
            feat.setGeometry(geom)
            valid_dt_layer_pr.addFeature(feat)
    else:
        feat = QgsFeature()
        feat.setGeometry(valid_delaunay)
        valid_dt_layer_pr.addFeature(feat)
    valid_dt_layer.startEditing()
    valid_dt_layer.commitChanges()
    valid_dt_layer.updateExtents()
    return valid_dt_layer

def create_median_line_opposite(vd_layer, layerA, layerB, crs):
    sp_index = QgsSpatialIndex(vd_layer)
    voronoi_a = []
    voronoi_b = []

    # Proses untuk fitur A
    for line in layerA.getFeatures():  # Ambil fitur dari layerA
        idx = sp_index.intersects(line.geometry().boundingBox())
        req = QgsFeatureRequest().setFilterFids(idx)
        req_feat = [feat for feat in vd_layer.getFeatures(req)]
        for feat in req_feat:
            if feat.geometry().intersects(line.geometry()):
                voronoi_a.append(feat.geometry())

    # Proses untuk fitur B
    for line in layerB.getFeatures():  # Ambil fitur dari layerB
        idx = sp_index.intersects(line.geometry().boundingBox())
        req = QgsFeatureRequest().setFilterFids(idx)
        req_feat = [feat for feat in vd_layer.getFeatures(req)]
        for feat in req_feat:
            if feat.geometry().intersects(line.geometry()):
                voronoi_b.append(feat.geometry())

    # Debugging: Periksa isi list
    print(f"Contents of voronoi_a: {len(voronoi_a)} geometries found")
    print(f"Contents of voronoi_b: {len(voronoi_b)} geometries found")

    # Gabungkan geometri dari voronoi_a jika tidak kosong
    if not voronoi_a:
        raise ValueError("voronoi_a is empty. Ensure valid input features for A.")
    
    combined_voronoi_a = QgsGeometry.unaryUnion(voronoi_a)  # Combine all geometries into one

    # Combine geometries from voronoi_b if not empty
    if not voronoi_b:
        raise ValueError("voronoi_b is empty. Ensure valid input features for B.")
    
    combined_voronoi_b = QgsGeometry.unaryUnion(voronoi_b)  # Combine all geometries into one

    # Dissolve geometries for combined Voronoi diagrams
    dissolve_voronoi_a = combined_voronoi_a.buffer(0, 5)
    dissolve_voronoi_b = combined_voronoi_b.buffer(0, 5)


    # Hitung median line
    median_line = dissolve_voronoi_a.intersection(dissolve_voronoi_b)

    # Debugging: Periksa median line
    if median_line.isEmpty():
        raise ValueError("Median line is empty after intersection.")

    median_layer = QgsVectorLayer("LineString?crs=" + crs, "Median Line", "memory")
    median_layer_pr = median_layer.dataProvider()
    
    # Add attributes (if needed)
    median_layer_pr.addAttributes([QgsField("name", QVariant.String)])
    median_layer.updateFields()

    # Add the median line geometry to the layer
    median_feat = QgsFeature()
    median_feat.setGeometry(median_line)
    median_feat.setAttributes(["Median Line"])
    
    median_layer_pr.addFeature(median_feat)

    # Finalize the layer
    median_layer.updateExtents()

    print("Median line layer created successfully.")
    
    return median_layer  # Return only the vector layer

def merge_layer_with_small_island(layer, small_island_layer):

    if layer is None or not isinstance(layer, QgsVectorLayer) or layer.isEmpty():
        print("Error: Provided layer is invalid or empty.")
        return None

    if small_island_layer is None or not isinstance(small_island_layer, QgsVectorLayer) or small_island_layer.isEmpty():
        print("Error: Small island layer is invalid or empty.")
        return None

    # Create a new merged layer in memory, using the same CRS as the input layers
    crs = layer.crs()  # Assume both layers have the same CRS
    merged_layer = QgsVectorLayer(f"Polygon?crs={crs.authid()}", "Merged Layer", "memory")
    merged_provider = merged_layer.dataProvider()

    # Start editing the merged layer
    merged_layer.startEditing()

    # Add existing features from the main layer

    # Extract geometry from the small island layer (assuming only one feature)
    for feature in layer.getFeatures():
        merged_provider.addFeature(feature)
    
    # Add features from layer2
    for feature in small_island_layer.getFeatures():
        merged_provider.addFeature(feature)

    # Create a feature for the small island and add it to the merged layer
    small_island_feature = QgsFeature()
    small_island_feature.setGeometry(small_island_geometry)
    merged_provider.addFeature(small_island_feature)

    # Commit changes to the merged layer
    merged_layer.commitChanges()

    return merged_layer



def apply_small_island_effect(median_line, small_island_geometry, effect_level):
    """
    Apply effects of a small island on the median line.

    Args:
        median_line (QgsGeometry): The original median line geometry.
        small_island_geometry (QgsGeometry): The geometry of the small island.
        effect_level (float): Effect level (0.0 = no effect, 0.5 = half effect, 1.0 = full effect).

    Returns:
        QgsGeometry: Modified median line geometry based on the effect level.
    """
    if effect_level == 0.0:
        # No effect, return original median line
        return median_line

    # Calculate the centroid of the small island
    island_centroid = small_island_geometry.centroid().asPoint()

    if effect_level == 1.0:
        # Full effect: Move the median line towards the island centroid
        modified_line = median_line.moveVertex(island_centroid.x(), island_centroid.y())
    else:
        # Half effect: Interpolate between original and modified position
        original_coords = median_line.asPolyline()
        modified_coords = []
        
        for point in original_coords:
            new_x = point.x() + (island_centroid.x() - point.x()) * effect_level
            new_y = point.y() + (island_centroid.y() - point.y()) * effect_level
            modified_coords.append(QgsPointXY(new_x, new_y))
        
        modified_line = QgsGeometry.fromPolylineXY(modified_coords)

    return modified_line
def create_median_line_adjacent(layerA, layerB, crs):
    # Create a spatial index for layerA
    sp_index = QgsSpatialIndex(layerA.getFeatures())
    
    median_lines = []

    # Process features from layerB
    for lineB in layerB.getFeatures():
        # Find potential adjacent lines in layerA
        adjacent_ids = sp_index.intersects(lineB.geometry().boundingBox())
        
        for lineA in layerA.getFeatures(adjacent_ids):
            # Check if the lines are adjacent (not intersecting)
            if lineA.geometry().touches(lineB.geometry()):
                # Calculate the median line
                median_line = QgsGeometry.unaryUnion([lineA.geometry(), lineB.geometry()]).centroid()
                median_lines.append(median_line)

    # Create a new vector layer for the median lines
    median_layer = QgsVectorLayer("LineString?crs=" + crs, "Median Lines", "memory")
    median_layer_pr = median_layer.dataProvider()
    
    # Add attributes (if needed)
    median_layer_pr.addAttributes([QgsField("name", QVariant.String)])
    median_layer.updateFields()

    # Add the median line geometries to the layer
    for median in median_lines:
        median_feat = QgsFeature()
        median_feat.setGeometry(median)
        median_feat.setAttributes(["Median Line"])
        median_layer_pr.addFeature(median_feat)

    # Finalize the layer
    median_layer.updateExtents()

    print("Median line layer created successfully.")
    
    return median_layer  # Return the vector layer

def create_equidistant_point(median_layer):
    equidistant_pt_layer = QgsVectorLayer(
        "Point?crs=" + median_layer.crs().authid(),
        "Equidistant Point",
        "memory"
    )
    equidistant_pt_layer_pr = equidistant_pt_layer.dataProvider()
    equidistant_pt_layer_pr.addAttributes([QgsField("id", QVariant.Int)])
    equidistant_pt_layer.updateFields()

    if len(median_layer.selectedFeatures()) > 0:
        list_geom = [
            feat.geometry() for feat in median_layer.selectedFeatures()
        ]
    else:
        list_geom = [
            feat.geometry() for feat in median_layer.getFeatures()
        ]

    point_id = 0
    for median_line_geom in list_geom:
        # Check if the geometry is a MultiLineString
        if median_line_geom.isMultipart():
            # Handle MultiLineString
            for line in median_line_geom.asMultiPolyline():  # Returns a list of LineStrings
                for point in line:
                    point_feat = QgsFeature()
                    point_feat.setGeometry(QgsGeometry.fromPointXY(point))
                    point_feat.setAttributes([point_id])
                    equidistant_pt_layer_pr.addFeature(point_feat)
                    point_id += 1
        else:
            # Handle LineString
            for point in median_line_geom.asPolyline():  # This works for LineStrings
                point_feat = QgsFeature()
                point_feat.setGeometry(QgsGeometry.fromPointXY(point))
                point_feat.setAttributes([point_id])
                equidistant_pt_layer_pr.addFeature(point_feat)
                point_id += 1

    equidistant_pt_layer.startEditing()
    equidistant_pt_layer.commitChanges()
    equidistant_pt_layer.updateExtents()
    return equidistant_pt_layer


def create_construction_line(vd_layer, equidistant_pt_layer, merged_pt_layer):
    cl_layer = QgsVectorLayer(
        "Linestring?crs=" + vd_layer.crs().authid(),
        "Construction Line",
        "memory"
    )
    cl_layer_pr = cl_layer.dataProvider()
    cl_layer_pr.addAttributes([QgsField("line_id", QVariant.Int)])
    cl_layer.updateFields()
    vd_index = QgsSpatialIndex(vd_layer)
    for feat in equidistant_pt_layer.getFeatures():
        intersect_idx = vd_index.intersects(feat.geometry().boundingBox())
        req = QgsFeatureRequest().setFilterFids(intersect_idx)
        req_feat = [feat for feat in vd_layer.getFeatures(req)]
        list_pid = []
        list_pt = []
        for f in req_feat:
            if f.geometry().intersects(feat.geometry()):
                pid = f["point_id"]
                list_pid.append(pid)
                pt_feat = [
                    feat
                    for feat in merged_pt_layer.getFeatures(
                        QgsFeatureRequest(
                            QgsExpression(f"\"point_id\" = '{pid}'")
                        )
                    )
                ]
                if len(pt_feat) == 1:
                    list_pt.append(pt_feat[0].geometry().asPoint())
        if len(list_pt) == 3:
            eq_pt = feat.geometry().asPoint()
            # create multilinestring feature
            cl_geom = QgsGeometry().fromMultiPolylineXY(
                [
                    [QgsPointXY(eq_pt), QgsPointXY(list_pt[0])],
                    [QgsPointXY(eq_pt), QgsPointXY(list_pt[1])],
                    [QgsPointXY(eq_pt), QgsPointXY(list_pt[2])],
                ]
            )
            cl_feat = QgsFeature()
            cl_feat.setGeometry(cl_geom)
            cl_feat.setAttributes([feat["id"]])
            cl_layer_pr.addFeature(cl_feat)
    cl_layer.startEditing()
    cl_layer.commitChanges()
    cl_layer.updateExtents()
    return cl_layer

def generate_final_boundary(
        list_feature_a,
        list_feature_b,
        boundary_distance_m,
        median_layer,
        crs,
        buffer_segment=1):
        # create buffer_a
        geom_a = list_feature_a[0].geometry()
        if len(list_feature_a) >= 1:
            for feat in list_feature_a[1:]:
                geom_a.addPartGeometry(feat.geometry())
        buffer_a = geom_a.buffer(boundary_distance_m, buffer_segment)
        # create buffer_b
        geom_b = list_feature_b[0].geometry()
        if len(list_feature_b) >= 1:
            for feat in list_feature_b[1:]:
                geom_b.addPartGeometry(feat.geometry())
        buffer_b = geom_b.buffer(boundary_distance_m, buffer_segment)
        # common area intersection
        common_area = buffer_a.intersection(buffer_b)
        
        # boundary polyline
        if buffer_a.isMultipart():
            boundaries_a = []
            for polygon in buffer_a.asMultiPolygon():
                boundaries_a.append(QgsGeometry.fromPolygonXY(polygon))
                boundary_a = QgsGeometry.unaryUnion(boundaries_a)  # Combine all polygons into one geometry
        else:
            boundary_a = QgsGeometry.fromPolygonXY(buffer_a.asPolygon())

        # Handle MultiPolygon for boundary_b
        if buffer_b.isMultipart():
            boundaries_b = []
            for polygon in buffer_b.asMultiPolygon():
                boundaries_b.append(QgsGeometry.fromPolygonXY(polygon))
                boundary_b = QgsGeometry.unaryUnion(boundaries_b)  # Combine all polygons into one geometry
        else:
            boundary_b = QgsGeometry.fromPolygonXY(buffer_b.asPolygon())
        # common line boundary
        median_line = [feat.geometry() for feat in median_layer.getFeatures()]
        if not median_line:
            raise ValueError("Median line geometries are empty. Ensure that the median layer has features.")
        line = median_line[0]
        if len(median_line) > 1:
            for geom in median_line[1:]:
                line.addPartGeometry(geom)
        common_line = line.intersection(common_area)
        # final boundary
        final_boundary_a = boundary_a.difference(buffer_b).combine(common_line)
        feat_a = QgsFeature()
        feat_a.setGeometry(final_boundary_a)
        final_boundary_b = boundary_b.difference(buffer_a).combine(common_line)
        feat_b = QgsFeature()
        feat_b.setGeometry(final_boundary_b)

        line_layer = QgsVectorLayer(
            "Linestring?crs=" + crs,
            'Boundary Layer',
            "memory"
        )
        line_layer_pr = line_layer.dataProvider()

        line_layer_pr.addFeature(feat_a)
        line_layer_pr.addFeature(feat_b)
        line_layer.startEditing()
        line_layer.commitChanges()
        return line_layer