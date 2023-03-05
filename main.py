import shelve
import time
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="FastNotes", description="FastNotes is a simple API application made with FastAPI to create and store your notes")


class NoteIn(BaseModel):
    title: str
    content: str


class NoteModal(BaseModel):
    id: int
    created_at: datetime
    title: str
    content: str


responses = {
    404: {"detail": "Note is not found"},
}

@app.post("/notes/", status_code=201, description="Create a new note with a title and content")
async def create_note(note: NoteIn) -> NoteModal:
    new_note = NoteModal(**note.dict(), id=round(time.time() * 1000), created_at=datetime.now())

    with shelve.open("notes", writeback=True) as notes:
        notes[str(new_note.id)] = new_note

    return new_note


@app.get("/notes/", description="Get a list of all notes created so far")
async def get_all_notes() -> list[NoteModal]:
    with shelve.open("notes") as notes:
        return list(notes.values())


@app.get("/notes/{note_id}", responses={**responses}, description="Get a note details based on the note ID")
async def get_note(note_id: int) -> NoteModal:
    with shelve.open("notes") as notes:
        try:
            note = notes[str(note_id)]
            return note
        except KeyError:
            raise HTTPException(status_code=404)


@app.delete("/notes/{note_id}", responses={**responses}, description="Deletes a note based on the note ID")
async def delete_note(note_id: int):
    with shelve.open("notes", writeback=True) as notes:
        try:
            del notes[str(note_id)]
            return {"message": "Note has been deleted"}
        except KeyError:
            raise HTTPException(status_code=404)


@app.put("/notes/{note_id}", responses={**responses}, description="Updates a note based on the note ID")
async def update_note(note_id: int, note:NoteIn) -> NoteModal:
    with shelve.open("notes", writeback=True) as notes:
        try:
            notes[str(note_id)].title = note.title
            notes[str(note_id)].content = note.content
            return notes[str(note_id)]
        except KeyError:
            raise HTTPException(status_code=404)