


select * from dbo.processing_events

select * from dbo.requests





select * from requests r 
left outer join processing_events p on r.request_id = p.request_id
where r.completed_at is null;


select * from requests r 
left  join processing_events p on r.request_id = p.request_id
where r.completed_at is null;