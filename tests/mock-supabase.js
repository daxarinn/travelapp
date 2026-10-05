// Browser-only fixture. No connection to the production Supabase project.
const localDate = d => new Date(d.getTime()-d.getTimezoneOffset()*60000).toISOString().slice(0,10);
const now = new Date();
const currentDate = localDate(now);
const later = new Date(now); later.setDate(later.getDate()+1);
window.testDB = {
  trip_members: [{user_id:'tester',trip_id:'trip'}],
  items: [
    {id:1,trip_id:'trip',title:'Morning event',category:'plan',planned_date:currentDate,planned_time:'09:00:00',notes:'All event details',done:false,starred:false,sort_order:10},
    {id:2,trip_id:'trip',title:'Evening event',category:'matur',planned_date:currentDate,planned_time:'18:00:00',notes:'Dinner',done:false,starred:false,sort_order:0},
    {id:3,trip_id:'trip',title:'Existing idea',category:'staður',planned_date:null,planned_time:null,notes:'Undated place',done:false,starred:false},
    {id:4,trip_id:'trip',title:'Tomorrow event',category:'plan',planned_date:localDate(later),planned_time:null,notes:'Tomorrow',done:false,starred:false},
    {id:5,trip_id:'trip',title:'Unscheduled time',category:'plan',planned_date:currentDate,planned_time:null,notes:null,done:false,starred:false}
  ],
  links:[{id:'link',trip_id:'trip',entity_type:'item',entity_id:'3',label:'Maps',url:'https://maps.google.com/',sort_order:10}],
  shopping_lists:[{id:'list',trip_id:'trip',title:'Groceries'}],
  shopping_items:[
    {id:'milk',trip_id:'trip',list_id:'list',title:'Milk',purchased:false,recurring_days:2},
    {id:'bread',trip_id:'trip',list_id:'list',title:'Bread',purchased:true,recurring_days:2,next_due_date:currentDate},
    {id:'coffee',trip_id:'trip',list_id:'list',title:'Coffee',purchased:true,recurring_days:2,next_due_date:localDate(later)}
  ],
  memos:[]
};
window.testWrites=[];
window.testMissingTime=false;
window.testMissingTravel=false;
class Query {
  constructor(table){this.table=table;this.filters=[];this.action='select';this.one=false}
  select(){return this}
  eq(k,v){this.filters.push([k,v]);return this}
  order(){return this}
  maybeSingle(){this.one=true;return this}
  single(){this.one=true;return this}
  update(data){this.action='update';this.payload=data;return this}
  insert(data){this.action='insert';this.payload=data;return this}
  delete(){this.action='delete';return this}
  then(resolve,reject){return Promise.resolve().then(()=>{
    if(window.testMissingTime&&this.payload&&'planned_time' in this.payload)return {data:null,error:{message:"Could not find the 'planned_time' column in the schema cache"}};
    if(window.testMissingTravel&&this.payload&&'travel_details' in this.payload)return {data:null,error:{message:"Could not find the 'travel_details' column in the schema cache"}};
    const rows=window.testDB[this.table];
    const matches=row=>this.filters.every(([k,v])=>String(row[k])===String(v));
    let result=rows.filter(matches);
    if(this.action==='update')result.forEach(row=>Object.assign(row,this.payload));
    if(this.action==='insert'){
      result=(Array.isArray(this.payload)?this.payload:[this.payload]).map((row,i)=>({id:this.table==='items'?100+rows.length+i:'new-'+rows.length+'-'+i,done:false,purchased:false,...row}));
      rows.push(...result);
    }
    if(this.action==='delete')window.testDB[this.table]=rows.filter(row=>!matches(row));
    if(this.action!=='select')window.testWrites.push({table:this.table,action:this.action,payload:this.payload});
    return {data:structuredClone(this.one?result[0]||null:result),error:null};
  }).then(resolve,reject)}
}
window.supabase={createClient:()=>({
  auth:{getSession:async()=>({data:{session:{user:{id:'tester'}}},error:null})},
  from:table=>new Query(table)
})};
