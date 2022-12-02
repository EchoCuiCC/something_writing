const obj2gltf = require("obj2gltf");
const fs = require("fs");

const source_fold = 'G:\\front_web\\cudes\\B-obj'
const output_fold = 'G:\\front_web\\cudes\\C-module'
const patient_list = 
['huangzeming_pre_CT',
 'lvlong_pre_CT',
 'maokuirong_pre_CT',
 'wuxingcai_pre_CT',
 'xuchaozhi_pre_CT',
 'xuwentou_pre_CT',
 'yaokai_pre_CT']
const parts = ['pelvis','aorta','right_common_iliac_artery','left_common_iliac_artery','right_external_iliac_artery','right_internal_iliac_artery','left_external_iliac_artery','left_internal_iliac_artery']
patient_list.map((patient)=>{
  parts.map((item,index)=>{
    obj2gltf(`${source_fold}\\${patient}\\${item}.obj`).then(function (gltf) {
        const data = Buffer.from(JSON.stringify(gltf));
        fs.writeFileSync(`${output_fold}\\${patient}\\${item}.gltf`, data);
      });
})
})


