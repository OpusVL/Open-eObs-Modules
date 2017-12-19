import csv
import re
hospitals = set()
wards = []


def slugify(string):
    string = string.lower()
    for character in [' ', '-', '.', '/', '&']:
        string = string.replace(character, '_')

    string = re.sub('\W', '', string)
    string = string.replace('_', ' ')
    string = re.sub('\s+', ' ', string)
    string = string.strip()
    string = string.replace(' ', '_')
    return string

with open('slam_wards.csv', 'rb') as wards_csv_file:
    raw_wards = csv.DictReader(wards_csv_file)
    for ward in raw_wards:
        hospitals.add(ward['Location'])
        wards.append(ward)

with open('slam_hospital_data.xml', 'wb') as hospital_file:
    hospital_file.write("""
    <openerp>
        <data>
    """)

    for hospital in hospitals:
        xml_id = slugify(hospital)

        hospital_file.write("""
            <!-- {name} Information -->
            <record id="nhc_{xml_id}_location_lh" model="nh.clinical.location">
                <field name="name">{name} POS Location</field>
                <field name="code">{xml_id}</field>
                <field name="type">pos</field>
                <field name="usage">hospital</field>
            </record>

            <record id="nhc_{xml_id}_location_lot_admission"
            model="nh.clinical.location">
                <field name="name">{name} Admission Location</field>
                <field name="code">adml_{xml_id}</field>
                <field name="type">structural</field>
                <field name="usage">room</field>
                <field name="parent_id" ref="nhc_{xml_id}_location_lh"/>
            </record>

            <record id="nhc_{xml_id}_location_lot_discharge"
            model="nh.clinical.location">
                <field name="name">{name} Discharge Location</field>
                <field name="code">disl_{xml_id}</field>
                <field name="type">structural</field>
                <field name="usage">room</field>
                <field name="parent_id" ref="nhc_{xml_id}_location_lh"/>
            </record>

            <record id="nhc_{xml_id}_pos_hospital" model="nh.clinical.pos">
                <field name="name">{name}</field>
                <field name="location_id" ref="nhc_{xml_id}_location_lh"/>
                <field name="company_id" ref="base.main_company"/>
                <field name="lot_admission_id"
                ref="nhc_{xml_id}_location_lot_admission"/>
                <field name="lot_discharge_id"
                ref="nhc_{xml_id}_location_lot_discharge"/>
            </record>
        """.format(xml_id=xml_id, name=hospital))

    hospital_file.write("""
        </data>
    </openerp>""")

for hospital in hospitals:
    file_slug = slugify(hospital)
    with open('slam_{slug}_wards.xml'.format(slug=file_slug),
              'wb') as hospital_wards_file:
        hospital_wards_file.write("""
        <openerp>
            <data>
        """)

for ward in wards:
    file_to_write = slugify(ward['Location'])
    xml_id = slugify(ward['Ward Name'])
    beds = int(ward['No of Beds'])
    beds += 1
    with open('slam_{file}_wards.xml'.format(file=file_to_write),
              'a') as hospital_wards_file:
        hospital_wards_file.write("""

        <!-- {name} Ward Location -->
        <record id="nh_eobs_{hospital}_location_{xml_id}"
        model="nh.clinical.location">
            <field name="name">{name}</field>
            <field name="code">{code}</field>
            <field name="parent_id" ref="nhc_{hospital}_location_lh"/>
            <field name="type">poc</field>
            <field name="context_ids"
            eval="[[6, False, [ref('nh_eobs.nh_eobs_context')]]]"/>
            <field name="usage">ward</field>
        </record>

        <!-- {name} Bed Locations -->
        """.format(hospital=file_to_write, xml_id=xml_id,
                   name=ward['Ward Name'].replace('&', '&amp;'),
                   code=ward['Ward Code']))

        for bed, index in enumerate(xrange(1, beds)):
            ind = str(index).zfill(2)
            code = xml_id + ind
            name = ward['Ward Name'].replace('&', '&amp;') + ' Bed ' + ind

            hospital_wards_file.write("""
        <record id="nh_eobs_{hospital}_location_{ward}_bed_{index}"
        model="nh.clinical.location">
            <field name="name">{name}</field>
            <field name="code">{code}</field>
            <field name="parent_id" ref="nh_eobs_{hospital}_location_{ward}"/>
            <field name="type">poc</field>
            <field name="context_ids"
            eval="[[6, False, [ref('nh_eobs.nh_eobs_context')]]]"/>
            <field name="usage">bed</field>
        </record>

            """.format(hospital=file_to_write, ward=xml_id, index=ind,
                       name=name, code=code))


for hospital in hospitals:
    file_slug = slugify(hospital)
    with open('slam_{slug}_wards.xml'.format(slug=file_slug),
              'a') as hospital_wards_file:
        hospital_wards_file.write("""
            </data>
        </openerp>
        """)
