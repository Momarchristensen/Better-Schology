interface Course {
  id: string;
  hasMaterials: boolean;
  name?: string;
}

interface CoursesResponse {
  status: "ok" | "error";
  courses: Course[];
  message?: string;
}
