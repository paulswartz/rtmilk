from datetime import date, timedelta
from uuid import uuid4

from pydantic import ValidationError
from pytest import mark, raises

def testClientDeleteWithNoDates(client):
	_ = client.Get('')
	taskAdded = client.Add(f'{uuid4()}')
	taskAdded.tags.Set({'tag1', 'tag2'})
	taskAdded.notes.Add('note title', 'note')
	taskAdded.Delete()

def testClientSync(client):
	with raises(ValidationError):
		client.Add(None)

	beforeTasks = client.Get('')

	name = f'name: {uuid4()}'
	task = client.Add(name)

	# Verify that 1 task was added
	allTasks = client.Get('')
	assert len(allTasks) == 1 + len(beforeTasks), allTasks

	# Set initial values of properties
	startDate = date.today()
	dueDate = startDate + timedelta(days=2)
	task.tags.Set({'tag1', 'tag2'})
	task.startDate.Set(startDate)
	task.dueDate.Set(dueDate)
	task.notes.Add('note title', 'note')

	# Verify that the new task has the expected values
	tasksWithTitle = client.Get(f'name:"{name}"')
	assert len(tasksWithTitle) == 1, tasksWithTitle
	newTask = tasksWithTitle[0]
	assert newTask.name.value == name
	assert sorted(newTask.tags.value) == ['tag1', 'tag2']
	assert newTask.startDate.value == startDate
	assert newTask.dueDate.value == dueDate
	assert newTask.complete.value is False

	# lastSync and lastModifiedTime works
	noTasks = client.Get('', lastSync=newTask.modifiedTime + timedelta(seconds=1))
	assert len(noTasks) == 0

	# Update some properties
	newTask.startDate.Set(dueDate)
	newTask.dueDate.Set(None)

	tasksWithTitle = client.Get(f'name:"{name}"')
	assert len(tasksWithTitle) == 1, f'Should be only 1 task with name: "{name}"\n{tasksWithTitle}'

	newTaskToo = tasksWithTitle[0]

	assert newTaskToo.startDate.value == dueDate, 'Start date should have been updated'
	assert newTaskToo.dueDate.value is None, 'Due date should have been updated'

	newTaskToo.Delete()

@mark.asyncio
async def testClientAsync(client):
	with raises(ValidationError):
		await client.AddAsync(None)

	beforeTasks = await client.GetAsync('')

	name = f'name: {uuid4()}'
	task = await client.AddAsync(name)

	# Verify that 1 task was added
	allTasks = await client.GetAsync('')
	assert len(allTasks) == 1 + len(beforeTasks), allTasks

	# Set initial values of properties
	startDate = date.today()
	dueDate = startDate + timedelta(days=2)
	await task.tags.SetAsync({'tag1', 'tag2'})
	await task.startDate.SetAsync(startDate)
	await task.dueDate.SetAsync(dueDate)
	await task.notes.AddAsync('note title', 'note')

	# Verify that the new task has the expected values
	tasksWithTitle = await client.GetAsync(f'name:"{name}"')
	assert len(tasksWithTitle) == 1, tasksWithTitle
	newTask = tasksWithTitle[0]
	assert newTask.name.value == name
	assert sorted(newTask.tags.value) == ['tag1', 'tag2']
	assert newTask.startDate.value == startDate
	assert newTask.dueDate.value == dueDate
	assert newTask.complete.value is False

	# lastSync and lastModifiedTime works
	noTasks = await client.GetAsync('', lastSync=newTask.modifiedTime + timedelta(seconds=1))
	assert len(noTasks) == 0

	# Update some properties
	await newTask.startDate.SetAsync(dueDate)
	await newTask.dueDate.SetAsync(None)

	tasksWithTitle = await client.GetAsync(f'name:"{name}"')
	assert len(tasksWithTitle) == 1, f'Should be only 1 task with name: "{name}"\n{tasksWithTitle}'

	newTaskToo = tasksWithTitle[0]

	assert newTaskToo.startDate.value == dueDate, 'Start date should have been updated'
	assert newTaskToo.dueDate.value is None, 'Due date should have been updated'

	await newTaskToo.DeleteAsync()
